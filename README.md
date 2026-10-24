# dijkstra-pq-bench

Binary heap vs Pairing heap vs Fibonacci heap, measured inside a real shortest-path workload

## Graph Representation

The graph is represented using **Compressed Sparse Row (CSR)** format. Flattening the adjacency
matrix into contiguous arrays for better CPU L1/L2 cache prefetching during edge relaxation.

## References

- [Compressed Sparse Row (CSR)](https://pnxguide.medium.com/compressed-sparse-row-motivation-and-explanation-cd92c71b7cfa)
