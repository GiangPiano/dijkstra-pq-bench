#ifndef DIJKSTRA_H
#define DIJKSTRA_H

#include <stddef.h>

#include "graph.h"

void dijkstra_dk(int* dist, Graph* g);
void dijkstra_lazy(int* dist, Graph* g);

#endif
