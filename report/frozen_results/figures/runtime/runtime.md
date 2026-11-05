# Dijkstra Priority Queue Benchmark Results

| Dataset | Mode | binary | brodal-okasaki | fibonacci | pairing |
|:---|:---| :---: | :---: | :---: | :---: |
| smoke_1k | Decrease-Key | 30.99 µs (±0.7%) | 228.21 µs (±0.4%) | 137.81 µs (±0.4%) | 46.95 µs (±0.6%) |
| smoke_1k | Lazy | 36.97 µs (±0.6%) | 184.16 µs (±0.3%) | 176.34 µs (±0.3%) | 58.05 µs (±0.8%) |
| uniform_sparse | Decrease-Key | 718.96 µs (±1.2%) | 3.46 ms (±1.5%) | 2.01 ms (±3.6%) | 925.24 µs (±0.7%) |
| uniform_sparse | Lazy | 873.17 µs (±0.5%) | 2.82 ms (±0.9%) | 2.36 ms (±0.7%) | 1.08 ms (±0.3%) |
| uniform_medium | Decrease-Key | 2.13 ms (±0.7%) | 16.24 ms (±0.7%) | 4.86 ms (±2.0%) | 3.10 ms (±1.2%) |
| uniform_medium | Lazy | 3.25 ms (±1.2%) | 10.49 ms (±1.0%) | 8.04 ms (±2.0%) | 4.84 ms (±1.6%) |
| uniform_dense | Decrease-Key | 1.69 ms (±4.2%) | 16.11 ms (±0.9%) | 3.08 ms (±4.2%) | 2.43 ms (±4.7%) |
| uniform_dense | Lazy | 3.18 ms (±3.1%) | 9.57 ms (±1.4%) | 7.04 ms (±2.3%) | 4.26 ms (±2.6%) |
| grid_224 | Decrease-Key | 2.40 ms (±0.5%) | 12.49 ms (±0.5%) | 7.23 ms (±1.1%) | 3.58 ms (±0.4%) |
| grid_224 | Lazy | 2.75 ms (±0.2%) | 10.13 ms (±2.8%) | 8.99 ms (±0.8%) | 4.14 ms (±0.4%) |
| hub_skewed | Decrease-Key | 1.54 ms (±0.5%) | 6.43 ms (±1.6%) | 4.09 ms (±1.2%) | 2.53 ms (±0.3%) |
| hub_skewed | Lazy | 1.72 ms (±0.5%) | 5.59 ms (±0.8%) | 4.52 ms (±0.9%) | 2.80 ms (±0.6%) |
| layered_frontier | Decrease-Key | 1.15 ms (±0.8%) | 11.97 ms (±0.8%) | 3.69 ms (±0.7%) | 2.08 ms (±0.2%) |
| layered_frontier | Lazy | 2.34 ms (±0.5%) | 8.10 ms (±1.0%) | 6.74 ms (±0.8%) | 3.39 ms (±0.3%) |
