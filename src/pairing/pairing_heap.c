#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>

#include "../heap.h"

typedef struct Node {
  Item item;            // Distance and vertex
  struct Node* child;   // Points to leftmost child
  struct Node* next;    // Points to right sibling
  struct Node* prev;    // Points to left sibling (or parent if first child)
} Node;

typedef struct Heap {
  Node* root;           // Point to root of the pairing heap
  size_t size;          // Total number of elements
} Heap;


// === MAIN HEAP FUNCTION ===

Heap* heap_create(size_t cap) {
  (void)cap;
  Heap* h = malloc(sizeof(Heap));
  if (!h) return NULL;
  h->root = NULL;
  h->size = 0;
  return h;
}

void heap_push(Heap* h, Item it) {
  if (!h) return;

  Node* n = malloc(sizeof(Node));
  if (!n) return;

  n->item  = it;
  n->child = NULL;
  n->next  = NULL;
  n->prev  = NULL;

  h->root = meld(h->root, n);
  h->size++;
}

Item heap_min(Heap* h) {
  assert(h != NULL && h->root != NULL);
  return h->root->item;
}

bool heap_empty(Heap* h) {
  return h == NULL || h->size == 0;
}

void heap_pop(Heap* h) {
  assert(h != NULL && h->root != NULL);

  Node* old_root = h->root;
  Node* children = old_root->child;

  free(old_root);
  h->size--;

  if (children == NULL) {
    h->root = NULL;
    return;
  }

  // Pass 1: Pair up siblings from left to right
  Node* head = NULL;
  Node* tail = NULL;
  Node* curr = children;

  while (curr != NULL) {
    Node* a = curr;
    Node* b = curr->next;
    Node* next_pair = NULL;

    if (b != NULL) {
      next_pair = b->next;
      b->next = NULL;
      b->prev = NULL;
    }
    a->next = NULL;
    a->prev = NULL;

    Node* pair = meld(a, b);

    if (head == NULL) {
      head = pair;
      tail = pair;
    } else {
      tail->next = pair;
      pair->prev = tail;
      tail = pair;
    }

    curr = next_pair;
  }

  // Pass 2: Meld paired trees from right to left
  Node* result = tail;
  while (result != NULL && result->prev != NULL) {
    Node* p = result->prev;
    Node* prev_of_p = p->prev;

    p->next = NULL;
    p->prev = NULL;
    result->next = NULL;
    result->prev = NULL;

    result = meld(p, result);
    result->prev = prev_of_p;
  }

  if (result != NULL) {
    result->next = NULL;
    result->prev = NULL;
  }

  h->root = result;
}

void heap_delete(Heap* h) {
  if (!h) return;

  if (h->root != NULL) {
    free_tree(h->root);
  }

  free(h);
}

// === HELPER FUNCTION ===

// Merges two pairing heaps. The root with smaller distance becomes parent.
static Node* meld(Node* a, Node* b) {
  if (!a) return b;
  if (!b) return a;

  if (a->item.distance > b->item.distance) {
    Node* tmp = a;
    a = b;
    b = tmp;
  }

  // Insert b as the leftmost child of a
  b->prev = a;
  b->next = a->child;
  if (a->child != NULL) {
    a->child->prev = b;
  }
  a->child = b;

  a->prev = NULL;
  a->next = NULL;

  return a;
}

// Recursively frees all nodes in an LCRS tree
static void free_tree(Node* n) {
  while (n != NULL) {
    Node* next = n->next;
    if (n->child != NULL) {
      free_tree(n->child);
    }
    free(n);
    n = next;
  }
}
