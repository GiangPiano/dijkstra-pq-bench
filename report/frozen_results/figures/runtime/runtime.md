# Dijkstra Priority Queue Benchmark Results

| Dataset | Mode | binary | brodal-okasaki | fibonacci | pairing |
|:---|:---| :---: | :---: | :---: | :---: |
| smoke_1k | Decrease-Key | 32.17 µs (±0.7%) | 227.27 µs (±0.4%) | 136.70 µs (±0.2%) | 46.28 µs (±0.7%) |
| smoke_1k | Lazy | 37.30 µs (±0.4%) | 184.36 µs (±0.3%) | 176.84 µs (±0.2%) | 56.29 µs (±0.5%) |
| uniform_sparse | Decrease-Key | 703.17 µs (±0.5%) | 3.41 ms (±0.7%) | 1.90 ms (±0.9%) | 920.36 µs (±0.6%) |
| uniform_sparse | Lazy | 850.70 µs (±0.2%) | 2.86 ms (±1.1%) | 2.34 ms (±0.2%) | 1.08 ms (±0.9%) |
| uniform_medium | Decrease-Key | 2.18 ms (±0.5%) | 15.88 ms (±0.9%) | 4.73 ms (±0.8%) | 2.96 ms (±0.4%) |
| uniform_medium | Lazy | 3.21 ms (±0.6%) | 10.32 ms (±0.3%) | 22.38 ms (±0.3%) | 4.40 ms (±0.2%) |
| uniform_dense | Decrease-Key | 1.63 ms (±2.1%) | 15.61 ms (±0.5%) | 7.96 ms (±1.2%) | 2.15 ms (±2.9%) |
| uniform_dense | Lazy | 3.01 ms (±1.6%) | 9.10 ms (±1.4%) | 19.15 ms (±1.4%) | 3.70 ms (±1.7%) |
| grid_224 | Decrease-Key | 2.43 ms (±0.4%) | 12.35 ms (±0.7%) | 20.96 ms (±0.5%) | 3.14 ms (±0.5%) |
| grid_224 | Lazy | 2.77 ms (±0.5%) | 9.83 ms (±0.2%) | 26.24 ms (±2.5%) | 3.54 ms (±0.6%) |
| hub_skewed | Decrease-Key | 1.53 ms (±0.3%) | 6.30 ms (±0.3%) | 11.61 ms (±0.7%) | 2.14 ms (±0.3%) |
| hub_skewed | Lazy | 1.72 ms (±0.5%) | 5.78 ms (±3.4%) | 13.47 ms (±0.9%) | 2.34 ms (±0.6%) |
| layered_frontier | Decrease-Key | 1.15 ms (±0.8%) | 11.89 ms (±0.1%) | 11.65 ms (±3.9%) | 1.71 ms (±0.4%) |
| layered_frontier | Lazy | 2.34 ms (±0.8%) | 7.96 ms (±0.2%) | 6.61 ms (±0.6%) | 2.80 ms (±1.1%) |
