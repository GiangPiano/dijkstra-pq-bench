#ifndef HEAP_H
#define HEAP_H

#include <stdbool.h>
#include <stddef.h>

typedef struct Heap Heap;

typedef struct Item {
  int distance;
  size_t vertex;
} Item;

struct Heap* heap_create(size_t n);
void heap_push(struct Heap* h, struct Item it);
struct Item heap_min(struct Heap* h);
bool heap_empty(struct Heap* h);
void heap_pop(struct Heap* h);
void heap_delete(struct Heap* h);

#endif
