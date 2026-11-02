/**
 * A stub non-working heap
 */

#include <stdlib.h>
#include "../heap.h"

typedef struct Heap {
  Item i;
} Heap;

Heap* heap_create(size_t cap) {
  (void)(cap);
  return NULL;
}

void heap_push(Heap* h, Item it) {
  (void)(h);
  (void)(it);
}

Item heap_min(Heap* h) {
  (void)(h);
  return (Item) {};
}

bool heap_empty(Heap* h) {
  (void)(h);
  return true;
}

void heap_pop(Heap* h) {
  (void)(h);
}

void heap_delete(Heap* h) {
  (void)(h);
}

void heap_decrease_key(Heap* h, Item it) {
  (void)(h);
  (void)(it);
}
