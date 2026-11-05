# Dijkstra Priority Queue Benchmark Results

| Dataset | Mode | binary | brodal-okasaki | fibonacci | pairing |
|:---|:---| :---: | :---: | :---: | :---: |
| smoke_1k | Decrease-Key | 31.32 µs (±0.7%) | 224.36 µs (±0.2%) | 137.00 µs (±0.4%) | 45.95 µs (±0.7%) |
| smoke_1k | Lazy | 36.98 µs (±0.6%) | 182.47 µs (±0.2%) | 175.32 µs (±0.3%) | 55.98 µs (±0.5%) |
| uniform_sparse | Decrease-Key | 703.57 µs (±0.5%) | 3.39 ms (±0.6%) | 1.96 ms (±1.1%) | 923.24 µs (±0.5%) |
| uniform_sparse | Lazy | 852.64 µs (±0.3%) | 2.76 ms (±0.5%) | 2.46 ms (±4.0%) | 1.08 ms (±0.3%) |
| uniform_medium | Decrease-Key | 2.13 ms (±0.5%) | 15.64 ms (±0.8%) | 4.79 ms (±1.0%) | 3.00 ms (±0.7%) |
| uniform_medium | Lazy | 3.23 ms (±0.9%) | 10.28 ms (±0.6%) | 7.98 ms (±2.4%) | 4.57 ms (±1.5%) |
| uniform_dense | Decrease-Key | 1.66 ms (±3.8%) | 15.64 ms (±0.7%) | 2.92 ms (±2.9%) | 2.18 ms (±3.1%) |
| uniform_dense | Lazy | 3.16 ms (±2.8%) | 9.28 ms (±2.2%) | 6.89 ms (±2.7%) | 3.83 ms (±2.5%) |
| grid_224 | Decrease-Key | 2.41 ms (±0.5%) | 12.19 ms (±0.3%) | 7.17 ms (±0.6%) | 3.07 ms (±0.6%) |
| grid_224 | Lazy | 2.76 ms (±0.8%) | 9.80 ms (±0.8%) | 9.00 ms (±1.3%) | 3.54 ms (±0.9%) |
| hub_skewed | Decrease-Key | 1.58 ms (±2.9%) | 6.38 ms (±0.8%) | 4.06 ms (±1.1%) | 2.15 ms (±0.4%) |
| hub_skewed | Lazy | 1.81 ms (±2.7%) | 5.54 ms (±0.6%) | 4.51 ms (±0.7%) | 2.33 ms (±0.4%) |
| layered_frontier | Decrease-Key | 1.18 ms (±0.6%) | 11.94 ms (±0.3%) | 3.67 ms (±0.8%) | 1.72 ms (±0.6%) |
| layered_frontier | Lazy | 2.33 ms (±0.4%) | 8.04 ms (±0.8%) | 6.64 ms (±0.4%) | 2.79 ms (±0.5%) |
