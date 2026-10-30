#ifndef HEAP_H
#define HEAP_H

#include <stdbool.h>
#include <stddef.h>

typedef struct Heap Heap;

typedef struct Item {
  int distance;
  size_t vertex;
} Item;

Heap* heap_create(size_t cap);
void heap_push(Heap* h, Item it);
Item heap_min(Heap* h);
bool heap_empty(Heap* h);
void heap_pop(Heap* h);
void heap_delete(Heap* h);
void heap_decrease_key(Heap* h, size_t v, int d);

#endif
