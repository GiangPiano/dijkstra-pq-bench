/*
 * A ""pure"" priority queue
 *
 * (Brodal-Okasaki priority queue)
 *
 * adapted from:
 * https://www.cambridge.org/core/services/aop-cambridge-core/content/view/1A799209383FD6535F90715192863C13/S095679680000201Xa.pdf/optimal_purely_functional_priority_queues.pdf
 * this implementation is not actually pure / persistant, as it would not be
 * usable with the djikstras implementation we are doing.
 *
 * instead, I've modified it to see how much we can optimise it without strongly
 * deviating from the original persistant data structure.
 *
 * Modifications:
 *
 * removed the meld operation as it isn't used in djikstras
 *
 * this meant also removing the forest field,
 * so the queue is no longer bootstrapped
 *
 * allocated the entire tree into a buffer,
 * our api allows for a single malloc for the buffer,
 * but this is designed so that the buffer could be reallocated
 * without invalidating the contents during copying
 */

#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "../heap.h"

// types

// when we store pointers into the buffer
// rather than store them as absolute addresses,
// we use relative addresses from the start of the buffer
// this type alias documents when such a relative address is used
// to deref them
// we need to also know the absolute address of the buffer
// and then its simple pointer arithmetic
typedef size_t RelativeTree;

// actual tree structure
struct Tree {
  Item it;
  size_t rank;
  RelativeTree child;
  RelativeTree sibling;
};

typedef struct Tree Tree;

struct Heap {
  Item pos_root;
  Item neg_root;
  // dynamic array cell buffer
  size_t cap;
  Tree* buf;
  // the positive queue
  RelativeTree pos;
  // the negative queue
  RelativeTree neg;
  // the free list
  RelativeTree free;
  bool pos_empty;
  bool neg_empty;
};

#define SENTINEL ((size_t)-1)

// all the functions take a heap pointer as a context
// as they need to be able to look up an address in the heap

// helpers for the relative addresses

// this is like if the pointer is null
static inline bool invalid(RelativeTree cell) { return cell == SENTINEL; }
// does the relative addressing
static inline Tree* deref(Heap* h, RelativeTree cell) { return &h->buf[cell]; }

// adapted from https://stackoverflow.com/questions/466204/rounding-up-to-next-power-of-2
// rounds up to the next power of 2
// compiler should loop unroll it
static inline size_t next_size(size_t size) {
  size--;
  for (size_t i = 1; i < sizeof(size_t) * CHAR_BIT; i *= 2) size |= size >> i;
  return ++size;
}

static void buf_realloc(Heap* h) {
  // free will now point to the start of the new list
  h->free    = h->cap;
  h->cap     = next_size(h->cap + 1);
  Tree* buf2 = realloc(h->buf, sizeof(Tree) * h->cap);
  if (buf2 == NULL) {
    fprintf(stderr, "Unable to reallocate buffer of size %zu.\n", h->cap);
    exit(EXIT_FAILURE);
  }
  h->buf = buf2;

  // initialise the new memory
  for (size_t i = h->free; i < h->cap - 1; i++) {
    h->buf[i].child = i + 1;
  }
  h->buf[h->cap - 1].child = SENTINEL;
}

// buffer free list management
static inline RelativeTree buf_alloc(Heap* h) {
  // if h->free is SENTINEL then we have no more free cells,
  // and need to reallocate the buffer
  if (invalid(h->free)) buf_realloc(h);
  RelativeTree next = h->free;
  h->free           = deref(h, next)->child;
  return next;
}
static inline void buf_free(Heap* h, RelativeTree cell) {
  deref(h, cell)->child = h->free;
  h->free               = cell;
}

// initialises cell as a rank 0 tree
static void rank0(Heap* h, RelativeTree cell, Item it) {
  Tree* actual    = deref(h, cell);
  actual->it      = it;
  actual->rank    = 0;
  actual->child   = SENTINEL;
  actual->sibling = SENTINEL;
}

// less than equal comparator for items
// is a total ordering
static bool lteq(Item l, Item r) {
  if (l.distance < r.distance) return true;
  if (l.distance == r.distance) return l.vertex <= r.vertex;
  return false;
}

// expects the ranks of q and r to match
static RelativeTree link(Heap* h, RelativeTree rel_q, RelativeTree rel_r) {
  Tree* q = deref(h, rel_q);
  Tree* r = deref(h, rel_r);

  if (lteq(q->it, r->it)) {
    q->rank++;
    r->sibling = q->child;
    q->child   = rel_r;
    return rel_q;
  } else {
    r->rank++;
    q->sibling = r->child;
    r->child   = rel_q;
    return rel_r;
  }
}

// we expect rel_t1 to be a rank 0 tree
static RelativeTree skew_link(Heap* h,
                              RelativeTree rel_t1,
                              RelativeTree rel_t2,
                              RelativeTree rel_t3) {
  Tree* t1 = deref(h, rel_t1);
  Tree* t2 = deref(h, rel_t2);
  Tree* t3 = deref(h, rel_t3);
  // t2 is the 'least'
  if (lteq(t2->it, t1->it) && lteq(t2->it, t3->it)) {
    t2->rank++;
    // add t1 and t3 to children
    t3->sibling = t2->child;
    t1->sibling = rel_t3;
    t2->child   = rel_t1;
    return rel_t2;
  }

  // t3 is the 'least'
  if (lteq(t3->it, t1->it) && lteq(t3->it, t2->it)) {
    t3->rank++;
    // add t1 and t2 to children
    t2->sibling = t3->child;
    t1->sibling = rel_t2;
    t3->child   = rel_t1;
    return rel_t3;
  }

  // t1 is the 'least'
  t1->rank    = t2->rank + 1;
  t2->sibling = rel_t3;
  t1->child   = rel_t2;
  t3->sibling = SENTINEL;
  return rel_t1;
}

// expects t to be a rank 0 tree
static RelativeTree add(Heap* h, RelativeTree t, RelativeTree ts) {
  if (invalid(ts)) {
    deref(h, t)->sibling = SENTINEL;
    return t;
  }

  Tree* t1 = deref(h, ts);
  if (invalid(t1->sibling)) {
    deref(h, t)->sibling = ts;
    return t;
  }

  Tree* t2 = deref(h, t1->sibling);
  if (t1->rank == t2->rank) {
    RelativeTree rest          = t2->sibling;
    RelativeTree t_prime       = skew_link(h, t, ts, t1->sibling);
    deref(h, t_prime)->sibling = rest;
    return t_prime;
  }

  deref(h, t)->sibling = ts;
  return t;
}

static RelativeTree ins(Heap* h, RelativeTree t, RelativeTree ts) {
  while (!invalid(ts) && deref(h, t)->rank >= deref(h, ts)->rank) {
    Tree* ts_tmp      = deref(h, ts);
    RelativeTree next = ts_tmp->sibling;
    ts_tmp->sibling   = SENTINEL;
    t                 = link(h, t, ts);
    ts                = next;
  }
  deref(h, t)->sibling = ts;
  return t;
}

static RelativeTree uniquify(Heap* h, RelativeTree ts) {
  if (invalid(ts)) return SENTINEL;
  Tree* ts_tmp      = deref(h, ts);
  RelativeTree next = ts_tmp->sibling;
  ts_tmp->sibling   = SENTINEL;
  return ins(h, ts, next);
}

static RelativeTree meld_unique(Heap* h, RelativeTree rel_qs, RelativeTree rel_rs) {
  if (invalid(rel_qs)) return rel_rs;
  if (invalid(rel_rs)) return rel_qs;

  Tree* qs = deref(h, rel_qs);
  Tree* rs = deref(h, rel_rs);

  if (qs->rank < rs->rank) {
    qs->sibling = meld_unique(h, qs->sibling, rel_rs);
    return rel_qs;
  }
  if (rs->rank < qs->rank) {
    rs->sibling = meld_unique(h, rs->sibling, rel_qs);
    return rel_rs;
  }

  RelativeTree ts = meld_unique(h, qs->sibling, rs->sibling);
  qs->sibling     = SENTINEL;
  rs->sibling     = SENTINEL;
  RelativeTree t  = link(h, rel_qs, rel_rs);
  return ins(h, t, ts);
}

static RelativeTree meld(Heap* h, RelativeTree qs, RelativeTree rs) {
  return meld_unique(h, uniquify(h, qs), uniquify(h, rs));
}

static RelativeTree extract_min(Heap* h, RelativeTree* ts) {
  // find the min tree,
  // then unlink it
  // min is a pointer to a relative tree
  RelativeTree* min = ts;
  // move on to the next immediately
  ts = &deref(h, *ts)->sibling;
  while (!invalid(*ts)) {
    // if ts is smaller than min
    // make min = ts
    Tree* t = deref(h, *ts);
    if (lteq(t->it, deref(h, *min)->it)) min = ts;
    ts = &t->sibling;
  }
  // the actual min relative tree
  RelativeTree rel_actual = *min;
  Tree* actual            = deref(h, rel_actual);
  // update the location that pointed to min
  // so that it points to min's sibling
  *min            = actual->sibling;
  actual->sibling = SENTINEL;
  return rel_actual;
}

static void split_ranks(Heap* h, RelativeTree* rank0, RelativeTree* rankn, RelativeTree rel_ts) {
  while (!invalid(rel_ts)) {
    Tree* ts          = deref(h, rel_ts);
    RelativeTree next = ts->sibling;
    if (ts->rank == 0) {
      ts->sibling = *rank0;
      *rank0      = rel_ts;
    } else {
      ts->sibling = *rankn;
      *rankn      = rel_ts;
    }
    rel_ts = next;
  }
}

// ts must not be invalid
static RelativeTree delete_min(Heap* h, RelativeTree ts, Item* min_it) {
  RelativeTree rel_min = extract_min(h, &ts);
  Tree* min            = deref(h, rel_min);

  RelativeTree rank0 = SENTINEL;
  RelativeTree rankn = SENTINEL;

  split_ranks(h, &rank0, &rankn, min->child);

  RelativeTree curr   = rank0;
  RelativeTree forest = meld(h, ts, rankn);
  while (!invalid(curr)) {
    RelativeTree next = deref(h, curr)->sibling;
    forest            = add(h, curr, forest);
    curr              = next;
  }

  *min_it = min->it;
  // put min's cell back on the free list
  buf_free(h, rel_min);
  return forest;
}

static void buf_free_all(Heap* h, RelativeTree rel_t) {
  if (invalid(rel_t)) return;
  Tree* t = deref(h, rel_t);
  buf_free_all(h, t->sibling);
  buf_free_all(h, t->child);
  buf_free(h, rel_t);
}

// remove invalid items from the negative queue
static void cancel_neg(Heap* h) {
  while (!h->pos_empty                                         //
         && !h->neg_empty                                      //
         && (h->neg_root.distance < h->pos_root.distance       //
             || (h->neg_root.distance == h->pos_root.distance  //
                 && h->neg_root.vertex < h->pos_root.vertex))) {
    if (invalid(h->neg)) {
      h->neg_empty = true;
      break;
    }
    h->neg = delete_min(h, h->neg, &h->neg_root);
  }
}

// cancel out the positive and negative queues
static void cancel(Heap* h) {
  cancel_neg(h);
  while (!h->pos_empty                                //
         && !h->neg_empty                             //
         && h->pos_root.vertex == h->neg_root.vertex  //
         && h->pos_root.distance == h->neg_root.distance) {
    if (invalid(h->pos)) {
      buf_free_all(h, h->neg);
      h->pos_empty = true;
      h->neg_empty = true;
      h->neg       = SENTINEL;
      break;
    }
    if (invalid(h->neg)) {
      h->neg_empty = true;
      h->pos       = delete_min(h, h->pos, &h->pos_root);
      break;
    }
    h->pos = delete_min(h, h->pos, &h->pos_root);
    h->neg = delete_min(h, h->neg, &h->neg_root);
    cancel_neg(h);
  }
}

Heap* heap_create(size_t cap) {
  Heap* h = malloc(sizeof(Heap));

  if (h == NULL) {
    fprintf(stderr, "Unable to allocate heap.\n");
    exit(EXIT_FAILURE);
  }

  h->pos_empty = true;
  h->neg_empty = true;
  h->cap       = cap;
  Tree* buf    = malloc(sizeof(Tree) * cap);

  if (cap > 0 && buf == NULL) {
    fprintf(stderr, "Unable to allocate buffer of size %zu.\n", cap);
    exit(EXIT_FAILURE);
  }

  h->buf = buf;

  h->pos = SENTINEL;
  h->neg = SENTINEL;


  if (cap == 0) {
    h->free = SENTINEL;
    return h;
  }

  // start the free list at 0
  h->free = 0;

  // link the free list
  // the children address shall be the successor
  for (size_t i = 0; i < cap - 1; i++) {
    buf[i].child = i + 1;
  }
  buf[cap - 1].child = SENTINEL;
  return h;
}

void heap_push(Heap* h, Item it) {
  if (h->pos_empty) {
    h->pos_root  = it;
    h->pos_empty = false;
    return;
  }

  RelativeTree t = buf_alloc(h);

  // smaller value becomes the root,
  // larger goes in the positive queue
  if (lteq(h->pos_root, it)) {
    rank0(h, t, it);
    h->pos = add(h, t, h->pos);
    return;
  }

  rank0(h, t, h->pos_root);
  h->pos      = add(h, t, h->pos);
  h->pos_root = it;

  // root changed, try to cancel
  cancel(h);
}

Item heap_min(Heap* h) { return h->pos_root; }
bool heap_empty(Heap* h) { return h->pos_empty; }

void heap_pop(Heap* h) {
  if (h->pos_empty) return;
  if (invalid(h->pos)) {
    buf_free_all(h, h->neg);
    h->pos_empty = true;
    h->neg_empty = true;
    h->neg       = SENTINEL;
    return;
  }
  h->pos = delete_min(h, h->pos, &h->pos_root);

  // cancel positive and negative roots
  cancel(h);
}

void heap_decrease_key(Heap* h, Item it, int distance) {
  // nothing in the heap
  if (h->pos_empty) return;

  // key is at the root
  if (h->pos_root.vertex == it.vertex && h->pos_root.distance == it.distance) {
    h->pos_root.distance = distance;
    return;
  }

  // theres no way it is in the queue
  if (invalid(h->pos)                          //
      || it.distance < h->pos_root.distance    //
      || (it.distance == h->pos_root.distance  //
          && it.vertex < h->pos_root.vertex))
    return;

  // no negatives
  if (h->neg_empty) {
    h->neg_root  = it;
    h->neg_empty = false;

    // push the new item into the queue
    heap_push(h, (Item){.distance = distance, .vertex = it.vertex});

    return;
  }


  RelativeTree t = buf_alloc(h);

  // smaller value becomes the root,
  // larger goes in the negative queue
  if (lteq(h->neg_root, it)) {
    rank0(h, t, it);
    h->neg = add(h, t, h->neg);

    // push the new item into the queue
    heap_push(h, (Item){.distance = distance, .vertex = it.vertex});

    return;
  }

  rank0(h, t, h->neg_root);
  h->neg      = add(h, t, h->neg);
  h->neg_root = it;

  // push the new item into the queue
  heap_push(h, (Item){.distance = distance, .vertex = it.vertex});
}

void heap_delete(Heap* h) {
  free(h->buf);
  free(h);
}
