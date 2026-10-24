#ifndef HEAP_H
#define HEAP_H

#include <stdbool.h>
#include <stddef.h>

typedef struct Heap {
  size_t size;
} Heap;

typedef struct Item {
  int distance;
  size_t vertex;
} Item;

Heap* heap_create(int n);
void heap_push(Heap* h, Item it);
Item heap_min(Heap* h);
bool heap_empty(Heap* h);
void heap_pop(Heap* h);
void heap_delete(Heap* h);

#endif
