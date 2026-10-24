#ifndef GRAPH_H
#define GRAPH_H

#include <stdlib.h>
#include <string.h>

typedef struct {
  int dest, weight;
} Edge;

typedef struct {
  int src, dest, weight;
} EdgeInput;

// Graph representation using CSR
// The 2D adjacency matrix is compressed into 3 arrays:
// - adj_start[]: storing the starting indices of node u in adj[]
// - adj[]: each node u owns a range [adj_start[u], adj_start[u + 1]), storing
//          the outgoing edges from node u in a contiguous segment
typedef struct {
  int num_vertices;
  int num_edges;
  int* adj_start;
  Edge* adj;
} Graph;

void free_graph(Graph* g);

Graph* build_graph(int num_vertices, int num_edges, const EdgeInput* edge_input);

#endif
