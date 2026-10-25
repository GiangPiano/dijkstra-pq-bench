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
  size_t size;
  size_t cap;
} Heap;

void heap_delete(Heap* h) {
  free(h->data);
  free(h);
}

Heap* heap_create(size_t cap) {
  if (cap == 0) cap = 16;

  Heap* h = malloc(sizeof(Heap));
  if (!h) return NULL;

  h->data = malloc(sizeof(Item) * cap);
  h->size = 0;
  h->cap  = cap;

  if (!h->data) {
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

static inline void swap(Item* a, Item* b) {
  Item* tmp = a;
  a         = b;
  b         = tmp;
}

static void bubble(Heap* h) {
  size_t i = h->size - 1;

  while (i > 0) {
    size_t p = (i - 1) / 2;
    if (h->data[p].distance <= h->data[i].distance) break;
    swap(&h->data[p], &h->data[i]);
    i = (i - 1) / 2;
  }
}

void heap_push(Heap* h, Item it) {
  if (h->size == h->cap) {
    h->cap *= 2;
    Item* tmp = realloc(h->data, h->cap * sizeof(Item));
    if (!tmp) return;

    h->data = tmp;
  }

  h->data[h->size] = it;
  h->size++;

  bubble(h);
}

static void sink(Heap* h) {
  int i = 0;
  while (true) {
    int l = (2 * i) + 1;
    int r = (2 * i) + 2;
    if (l < h->size && h->data[i].distance < h->data[l].distance)
      swap(&h->data[i], &h->data[l]);
    else if (r < h->size && h->data[i].distance > h->data[r].distance)
      swap(&h->data[i], &h->data[r]);
    else
      break;
  }
}

void heap_pop(Heap* h) {
  assert(h->size > 0);

  h->data[0] = h->data[--h->size];

  sink(h);
}

Item heap_min(Heap* h) {
  assert(h->size > 0);
  return h->data[0];
}

bool heap_empty(Heap* h) { return h->size == 0; }
