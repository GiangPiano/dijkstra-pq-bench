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
 * instead, I've hand optimised it to re-use the allocations as much as
 * possible.
 */

#include <stdlib.h>
#include "../heap.h"

// type defs

// forward ref
typedef struct TreeList TreeList;

// actual tree structure
typedef struct Tree {
  Item it;
  TreeList* forest;
  size_t rank;
  TreeList* children;
} Tree;

// linked list of trees
typedef struct TreeList {
	Tree car;
	TreeList* cdr;
} TreeList;

// tree list functions

// mutates cell or allocates if its NULL
static TreeList* tree_list_recons(TreeList* cell, Tree car, TreeList* cdr) {
  if (cell == NULL) cell = malloc(sizeof(TreeList));
	cell->car = car;
	cell->cdr = cdr;
	return cell;
}

// frees just one cell
static void tree_list_delete(TreeList* ls) {
  if (ls != NULL) free(ls);
}

// forward ref
static void delete_tree(Tree t);
static void tree_list_delete_all(TreeList* ts) {
  while (ts != NULL) {
    delete_tree(ts->car);
    TreeList* cdr = ts->cdr;
    free(ts);
    ts = cdr;
  }
}

// internal tree functions

// single element queue
static Tree singleton_forest(Item it, TreeList* forest) {
  return (Tree) { it, forest, 0, NULL };
}

// less than equal comparator for items
static bool lteq(Item l, Item r) {
  return l.distance <= r.distance;
}

// expects the ranks of q and r to match
// will mutate cell or alloc
static Tree link_forest(TreeList* cell, Tree q, Tree r) {
  if (lteq(q.it, r.it)) {
    q.rank++;
    q.children = tree_list_recons(cell, r, q.children);
    return q;
  }
  else {
    r.rank++;
    r.children = tree_list_recons(cell, q, r.children);
    return r;
  }
}

static Tree skew_link_forest(
    TreeList* cell1,
    TreeList* cell2,
    Item it,
    Tree t1,
    Tree t2) {
  // t1 is the 'least'
  if (lteq(t1.it, it) && lteq(t1.it, t2.it)) {
    t1.rank++;
    // add it and t2 to children
    t1.children = tree_list_recons(
        cell1,
        singleton_forest(it, NULL),
        tree_list_recons(cell2, t2, t1.children));
    return t1;
  }
  // t2 is the 'least'
  if (lteq(t2.it, it) && lteq(t2.it, t1.it)) {
    t2.rank++;
    // add it and t1 to children
    t2.children = tree_list_recons(
        cell1,
        singleton_forest(it, NULL),
        tree_list_recons(cell2, t1, t2.children));
    return t2;
  }
  // it is the 'least'
  return (Tree) {
    it,
    NULL,
    t1.rank + 1,
    tree_list_recons(cell1, t1, tree_list_recons(cell2, t2, NULL)),
  };
}

//
static TreeList* ins_forest(TreeList* cell, Tree t, TreeList* ts) {
  while (ts != NULL && t.rank >= ts->car.rank) {
    // pull out cdr so we don't lose it
    TreeList* cdr = ts->cdr;
    t = link_forest(ts, t, ts->car);
    ts = cdr;
  }
  return tree_list_recons(cell, t, ts);
}

static TreeList* uniquify_forest(TreeList* ts) {
  if (ts == NULL) return NULL;
  return ins_forest(ts, ts->car, ts->cdr);
}

static TreeList* meld_unique_forest(TreeList* qs, TreeList* rs) {
  if (qs == NULL) return rs;
  if (rs == NULL) return qs;
  if (qs->car.rank < rs->car.rank) {
    qs->cdr = meld_unique_forest(qs->cdr, rs);
    return qs;
  }
  if (rs->car.rank < qs->car.rank) {
    rs->cdr = meld_unique_forest(qs, rs->cdr);
    return rs;
  }

  TreeList* ts = meld_unique_forest(qs->cdr, rs->cdr);
  Tree t = link_forest(rs, qs->car, rs->car);
  return ins_forest(qs, t, ts);
}

static TreeList* meld_forest(TreeList* qs, TreeList* rs) {
  return meld_unique_forest(uniquify_forest(qs), uniquify_forest(rs));
}

// expects t to be a rank 0 forest
static TreeList* add_forest(TreeList* cell, Item it, TreeList* ts) {
  if (ts == NULL || ts->cdr == NULL) return tree_list_recons(
      cell,
      singleton_forest(it, NULL),
      ts);

  Tree t1 = ts->car;
  Tree t2 = ts->cdr->car;
  TreeList* rest = ts->cdr->cdr;

  if (t1.rank == t2.rank) return tree_list_recons(
      cell,
      skew_link_forest(ts, ts->cdr, it, t1, t2),
      rest);
  return tree_list_recons(cell, singleton_forest(it, NULL), ts);
}

// splits forest into (min element, other elements)
// the ts cell passed into this is always free to reallocate afterwards
static void split_min_forest(Tree* min, TreeList** others, TreeList* ts) {
  if (ts->cdr == NULL) {
    *min = ts->car;
    *others = NULL;
    return;
  }
  Tree t = ts->car;
  split_min_forest(min, others, ts->cdr);
  // t is smaller
  if (lteq(t.it, min->it)) {
    *others = tree_list_recons(ts->cdr, *min, *others);
    *min = t;
    return;
  }
  // min is smaller
  *others = tree_list_recons(ts->cdr, t, *others);
}

// splits forest into rank 0 and not rank 0
static void split_forest(TreeList** rank0, TreeList** rankn, TreeList* ts) {
  while (ts != NULL) {
    Tree car = ts->car;
    TreeList* cdr = ts->cdr;
    if (car.rank == 0) *rank0 = tree_list_recons(ts, car, *rank0);
    else *rankn = tree_list_recons(ts, car, *rankn);
    ts = cdr;
  }
}

// ts must not be NULL
static Tree delete_min_forest(TreeList* ts) {
  Tree min;
  TreeList* others;

  split_min_forest(&min, &others, ts);

  // free the first cell in ts that will now be unused
  tree_list_delete(ts);

  TreeList* rank0 = NULL;
  TreeList* rankn = NULL;

  split_forest(&rank0, &rankn, min.children);

  TreeList* curr = rank0;
  TreeList* forest = meld_forest(others, rankn);
  while (curr != NULL) {
    Tree car = curr->car;
    TreeList* cdr = curr->cdr;
    forest = add_forest(curr, car.it, forest);
    curr = cdr;
  }

  return singleton_forest(min.it, meld_forest(min.forest, forest));
}

static void delete_tree(Tree t) {
  tree_list_delete_all(t.forest);
  tree_list_delete_all(t.children);
}

// imperative heap api

struct Heap {
  bool empty;
  Item it;
  TreeList* forest;
};

Heap* heap_create(size_t cap) {
  // we don't care about the size, this prevents an unused warning
  (void)(cap);
  Heap* h = malloc(sizeof(Heap));
  h->empty = true;
  return h;
}

void heap_push(Heap* h, Item it) {
  // empty, make it the root
  if (h->empty) {
    h->it = it;
    h->forest = NULL;
    h->empty = false;
    return;
  }

  // make h->it the root
  if (lteq(h->it, it)) {
    // no space credit, will allocate
    h->forest = add_forest(NULL, it, h->forest);
    return;
  }

  // make it the root
  TreeList* forest = add_forest(
      // no space credit, will allocate
      NULL,
      h->it,
      h->forest);
  h->it = it;
  h->forest = forest;
}

Item heap_min(Heap* h) { return h->it; }

bool heap_empty(Heap* h) { return h->empty; }

void heap_pop(Heap* h) {
  if (h->empty) return;
  if (h->forest == NULL) {
    h->empty = true;
    return;
  }
  Tree min = delete_min_forest(h->forest);
  h->it = min.it;
  h->forest = min.forest;
}

static bool decrease_tree(Tree* t, Item it) {
  if (t->it.vertex == it.vertex) {
    if (it.distance < t->it.distance) {
      t->it.distance = it.distance;
    }
    return true;
  }
  TreeList* curr = t->children;
  while (curr != NULL) {
    if (decrease_tree(&curr->car, it)) {
      if (lteq(curr->car.it, t->it)) {
        Item tmp = t->it;
        t->it = curr->car.it;
        curr->car.it = tmp;
      }
      return true;
    }
    curr = curr->cdr;
  }
  curr = t->forest;
  while (curr != NULL) {
    if (decrease_tree(&curr->car, it)) {
      return true;
    }
    curr = curr->cdr;
  }
  return false;
}

static bool decrease_forest(TreeList* ts, Item it, Tree** min_tree) {
  TreeList* curr = ts;
  while (curr != NULL) {
    if (decrease_tree(&curr->car, it)) {
      if (min_tree) *min_tree = &curr->car;
      return true;
    }
    curr = curr->cdr;
  }
  return false;
}

void heap_decrease_key(Heap* h, Item it) {
  if (!h || h->empty) return;
  if (h->it.vertex == it.vertex) {
    if (it.distance < h->it.distance) {
      h->it.distance = it.distance;
    }
    return;
  }
  Tree* found_tree = NULL;
  if (decrease_forest(h->forest, it, &found_tree)) {
    if (found_tree && lteq(found_tree->it, h->it)) {
      Item tmp = h->it;
      h->it = found_tree->it;
      found_tree->it = tmp;
    }
  }
}

void heap_delete(Heap* h) {
  if (!h) return;
  if (!h->empty) {
    tree_list_delete_all(h->forest);
  }
  free(h);
}
