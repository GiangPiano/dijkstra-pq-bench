#include <stdbool.h>
#include <stdlib.h>
#include <assert.h>
#include "../heap.h"

#define MAX_DEGREE 64

typedef struct Node {
  Item item;            // Distance and vertex
  int degree;           // Number of children this node has
  bool marked;          // Tracker to prevent cutting more than 2 children
  struct Node* parent;  // Point to the parent
  struct Node* child;   // Point to any child in this node's children
  struct Node* left;    // Left sibling
  struct Node* right;   // Right sibling
} Node;

typedef struct Heap {
  Node* min;    // Point to the root node with the minimum key
  size_t size;  // Total number of node in the heap
  Node** pos;   // Vertex -> Node mapping for decrease_key
  size_t pos_cap; // Capacity of pos array
} Heap;

// Some helper function needed in this case
static void link_child(Node* y, Node* x);
static void consolidate(Heap* h);
static void free_tree(Node* n);
static void cut(Heap* h, Node* x, Node* y);
static void cascading_cut(Heap* h, Node* y);

// === MAIN HEAP FUNCTION ===

Heap* heap_create(size_t cap) {
  if (cap == 0) cap = 16;
  Heap* h = malloc(sizeof(Heap));
  if (!h) return NULL;
  h->min  = NULL;
  h->size = 0;
  h->pos_cap = cap;
  h->pos = calloc(cap, sizeof(Node*));
  if (!h->pos) {
    free(h);
    return NULL;
  }
  return h;
}

void heap_push(Heap* h, Item it) {
  if (!h) return;

  if (it.vertex >= h->pos_cap) {
    size_t new_cap = (it.vertex + 1 > h->pos_cap * 2) ? it.vertex + 1 : h->pos_cap * 2;
    Node** new_pos = realloc(h->pos, new_cap * sizeof(Node*));
    if (!new_pos) return;
    for (size_t i = h->pos_cap; i < new_cap; i++) new_pos[i] = NULL;
    h->pos = new_pos;
    h->pos_cap = new_cap;
  }

  // 1. Allocate and initialise the new node
  Node* n = malloc(sizeof(Node));
  if (!n) return;

  n->item   = it;
  n->degree = 0;
  n->marked = false;
  n->parent = NULL;
  n->child  = NULL;
  h->pos[it.vertex] = n;

  // 2. Add the node to the root list
  if (h->min == NULL) {
    // The heap was empty, node is the only root, looping to itself
    n->left  = n;
    n->right = n;
    h->min   = n;
  } else {
    // Splice n into the circular root list next to h->min
    n->right            = h->min->right;
    n->left             = h->min;
    h->min->right->left = n;
    h->min->right       = n;

    // 3. Update min if the new node has a smaller distance
    if (n->item.distance < h->min->item.distance) {
      h->min = n;
    }
  }

  // 4. Increment the total node count
  h->size++;
}

Item heap_min(Heap* h) {
  assert(h != NULL && h->min != NULL);
  return h->min->item;
}

bool heap_empty(Heap* h) {
  return h == NULL || h->size == 0;
}

void heap_pop(Heap* h) {
  assert(h != NULL && h->min != NULL);

  Node* z = h->min;

  // 1. Promote all children of z to the root list
  if (z->child != NULL) {
    Node* curr = z->child;
    for (int i = 0; i < z->degree; i++) {
      Node* next          = curr->right;
      curr->parent        = NULL;
      // Splice curr into the root list next to z
      curr->left          = z;
      curr->right         = z->right;
      z->right->left      = curr;
      z->right            = curr;
      curr = next;
    }
  }

  // 2. Remove z from the root list
  if (z->right == z) {
    // z was the only node in the entire heap
    h->min = NULL;
  } else {
    z->left->right = z->right;
    z->right->left = z->left;
    h->min         = z->right; // temporary min, consolidate will find the true min
    consolidate(h);
  }

  // 3. Free memory and decrement size
  if (z->item.vertex < h->pos_cap) {
    h->pos[z->item.vertex] = NULL;
  }
  free(z);
  h->size--;
}

void heap_delete(Heap* h) {
  if (!h) return;

  // Free all nodes in the root list and their subtrees
  if (h->min != NULL) {
    free_tree(h->min);
  }

  // Free the heap wrapper itself
  free(h->pos);
  free(h);
}

static void cut(Heap* h, Node* x, Node* y) {
  // 1. Remove x from y's circular child list
  if (x->right == x) {
    y->child = NULL;
  } else {
    x->left->right = x->right;
    x->right->left = x->left;
    if (y->child == x) {
      y->child = x->right;
    }
  }
  y->degree--;

  // 2. Add x to the root list next to h->min
  x->right            = h->min->right;
  x->left             = h->min;
  h->min->right->left = x;
  h->min->right       = x;

  x->parent = NULL;
  x->marked = false;
}

static void cascading_cut(Heap* h, Node* y) {
  Node* z = y->parent;
  if (z != NULL) {
    if (!y->marked) {
      y->marked = true;
    } else {
      cut(h, y, z);
      cascading_cut(h, z);
    }
  }
}

void heap_decrease_key(Heap* h, Item it, int new_distance) {
  if (!h || it.vertex >= h->pos_cap) return;
  Node* x = h->pos[it.vertex];
  if (!x) return;
  assert(new_distance <= x->item.distance);

  x->item.distance = new_distance;
  Node* y = x->parent;

  if (y != NULL && x->item.distance < y->item.distance) {
    cut(h, x, y);
    cascading_cut(h, y);
  }

  if (x->item.distance < h->min->item.distance) {
    h->min = x;
  }
}

// === HELPER FUNCTION ===

// Link tree rooted at y as a child of tree rooted at x
static void link_child(Node* y, Node* x) {
  y->parent = x;
  if (x->child == NULL) {
    x->child = y;
    y->left  = y;
    y->right = y;
  } else {
    // Splice y into x's circular child list
    y->right              = x->child->right;
    y->left               = x->child;
    x->child->right->left = y;
    x->child->right       = y;
  }
  x->degree++;
  y->marked = false;
}

// Combine trees of equal degree until every root has a unique degree
static void consolidate(Heap* h) {
  Node* A[MAX_DEGREE] = {NULL};

  // 1. Break circular root list into a linear NULL-terminated list
  h->min->left->right = NULL;
  Node* curr = h->min;

  while (curr != NULL) {
    Node* next = curr->right;
    Node* x    = curr;
    int d      = x->degree;

    // Isolate x as a standalone tree
    x->left  = x;
    x->right = x;

    // Merge with existing trees in A[] of the same degree
    while (d < MAX_DEGREE && A[d] != NULL) {
      Node* y = A[d];
      if (x->item.distance > y->item.distance) {
        Node* tmp = x;
        x = y;
        y = tmp;
      }
      link_child(y, x);
      A[d] = NULL;
      d++;
    }
    A[d] = x;
    curr = next;
  }

  // 2. Rebuild the circular root list from A[]
  h->min = NULL;
  for (int i = 0; i < MAX_DEGREE; i++) {
    if (A[i] != NULL) {
      if (h->min == NULL) {
        h->min      = A[i];
        A[i]->left  = A[i];
        A[i]->right = A[i];
      } else {
        A[i]->right         = h->min->right;
        A[i]->left          = h->min;
        h->min->right->left = A[i];
        h->min->right       = A[i];

        if (A[i]->item.distance < h->min->item.distance) {
          h->min = A[i];
        }
      }
    }
  }
}

static void free_tree(Node* n) {
  if (n == NULL) return;

  // 1. Break the circular sibling list into a linear NULL-terminated list
  n->left->right = NULL;

  Node* curr = n;
  while (curr != NULL) {
    Node* next = curr->right;

  // 2. Recursively free all children of this node
    if (curr->child != NULL) {
      free_tree(curr->child);
    }

	// 3. Free the node itself
    free(curr);
    curr = next;
  }
}
