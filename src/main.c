#include <stdio.h>

#include "dijkstra.h"
#include "graph.h"

int main(int argc, char* argv[]) {
  printf("Hello, World\n");

  int num_vertices   = 4;
  EdgeInput edges[5] = {{0, 1, 4}, {0, 2, 2}, {1, 2, 1}, {1, 3, 5}, {2, 3, 8}};

  Graph* g = build_graph(num_vertices, 5, edges);

  int* dist = dijkstra(g, 0);

  for (int i = 0; i < num_vertices; i++) {
    printf("%d ", dist[i]);
  }

  free_graph(g);

  return 0;
}
