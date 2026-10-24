#include <stdio.h>

#include "graph.h"

int main(int argc, char* argv[]) {
  printf("Hello, World\n");

  EdgeInput edges[5] = {{0, 1, 4}, {0, 2, 2}, {1, 2, 1}, {1, 3, 5}, {2, 3, 8}};

  Graph* g = build_graph(5, 5, edges);

  return 0;
}
