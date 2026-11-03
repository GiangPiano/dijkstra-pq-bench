/*
 * Binary heap
 * A binary tree. Balancing on insertion/deletion via bubbling and sinking
 * Representing tree in array[]
 * - left node of i-> arr[2 * i + 1] // 2 * i will not work for i = 0
 * - right node of i-> arr[2 * i + 2]
 *
 * min() -> return arr[0]
 * insert()
 */

#include <assert.h>
#include <stdlib.h>

#include "../heap.h"

typedef struct Heap {
  Item* data;
  size_t* pos;  // keeping track of the index for heap_decrease_key
  size_t size;
  size_t cap;
} Heap;

void heap_delete(Heap* h) {
  if (!h) return;
  free(h->data);
  free(h->pos);
  free(h);
}

Heap* heap_create(size_t cap) {
  if (cap == 0) cap = 16;

  Heap* h = malloc(sizeof(Heap));
  if (!h) return NULL;

  h->data = malloc(sizeof(Item) * cap);
  h->pos  = malloc(sizeof(size_t) * cap);
  h->size = 0;
  h->cap  = cap;

  if (!h->data || !h->pos) {
    heap_delete(h);
    return NULL;
  }

  return h;
}

// 1.Insert the new element at the end of the heap.
// 2.Initialize i as the index of the new element.
// // bubble
// 3.WHILE i is not 0 AND heap[parent(i)] > heap[i]
// 4.SWAP heap[i] and heap[parent(i)]
// 5.Update i to parent(i)


static void bubble(Heap* h, size_t i) {
  Item moving = h->data[i];

  while (i > 0) {
    size_t p = (i - 1) / 2;
    if (h->data[p].distance <= moving.distance) break;

    h->data[i]                = h->data[p];  // Copying the parent node to the current node
    h->pos[h->data[i].vertex] = i;           // Update the position of the new node
    i                         = p;           // Moving to the parent
  }

  h->data[i]            = moving;  // Placing the new item at the final position
  h->pos[moving.vertex] = i;
}

void heap_push(Heap* h, Item it) {
  // Expanding the capacity on full
  if (h->size == h->cap) {
    size_t new_cap = 2 * h->cap;
    Item* tmp      = realloc(h->data, new_cap * sizeof(Item));
    if (!tmp) return;
    h->data = tmp;

    size_t* pos_tmp = realloc(h->pos, new_cap * sizeof(size_t));
    if (!pos_tmp) return;
    h->pos = pos_tmp;

    h->cap = new_cap;
  }

  h->data[h->size] = it;  // appending the new item to the end
  bubble(h, h->size);     // then bubble it up to its appropriate position
  h->size++;
}

static void sink(Heap* h, size_t i) {
  Item moving = h->data[i];

  while (true) {
    // Set the minimum distance (best) found to the current item.
    // At each level, compare best to it's left and right child
    // and move to that direction.
    size_t l = (2 * i) + 1;
    size_t r = (2 * i) + 2;
    size_t m = i;                // index of the smallest of moving, l, r
    int best = moving.distance;  // smallest distance seen so far

    //  if best < left_child -> bubble the left child to the current
    //  if best > right_child -> bubble the right child to the current
    if (l < h->size && h->data[l].distance < best) {
      m    = l;
      best = h->data[l].distance;
    }
    if (r < h->size && h->data[r].distance < best) {
      m = r;
    }
    if (m == i) break;

    //  move down and repeat, to find the lowest possible position for
    //  the item
    h->data[i]                = h->data[m];
    h->pos[h->data[i].vertex] = i;
    i                         = m;
  }

  // finally, place the item at this bottom position
  h->data[i]            = moving;
  h->pos[moving.vertex] = i;
}

// We need to pop h->data[0].
// We copy the bottom item to the top, then decrement h->size to exclude
// that item from the list.
// Since the bottom item should be placed at the back, it needs to be
// sunk down to its appropriate position.
void heap_pop(Heap* h) {
  assert(h->size > 0);
  h->size--;
  if (h->size > 0) {
    h->data[0] = h->data[h->size];  // h->size is now the index of the last item
    sink(h, 0);
  }
}

// simply return the first element
Item heap_min(Heap* h) {
  assert(h->size > 0);
  return h->data[0];
}

void heap_decrease_key(Heap* h, Item it, int new_distance) {
  size_t i = h->pos[it.vertex];
  assert(i < h->size);  // vertex must currently be in the heap
  assert(h->data[i].vertex == it.vertex);
  assert(new_distance <= h->data[i].distance);
  h->data[i].distance = new_distance;
  bubble(h, i);
}

bool heap_empty(Heap* h) { return h->size == 0; }
