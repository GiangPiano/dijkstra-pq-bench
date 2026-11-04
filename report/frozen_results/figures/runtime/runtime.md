# Dijkstra Priority Queue Benchmark Results

| Dataset | Mode | binary | brodal-okasaki | fibonacci | pairing |
|:---|:---| :---: | :---: | :---: | :---: |
| smoke_1k | Decrease-Key | 30.13 µs (±0.7%) | 225.84 µs (±0.8%) | 160.11 µs (±2.6%) | 45.25 µs (±0.6%) |
| smoke_1k | Lazy | 36.19 µs (±0.6%) | 174.55 µs (±0.2%) | 177.40 µs (±0.2%) | 57.07 µs (±0.9%) |
| uniform_sparse | Decrease-Key | 699.68 µs (±0.3%) | 3.39 ms (±0.5%) | 1.90 ms (±0.2%) | 918.19 µs (±0.6%) |
| uniform_sparse | Lazy | 890.17 µs (±2.3%) | 2.74 ms (±0.4%) | 2.35 ms (±0.5%) | 1.15 ms (±4.4%) |
| uniform_medium | Decrease-Key | 2.12 ms (±0.6%) | 15.43 ms (±0.4%) | 4.82 ms (±1.2%) | 2.95 ms (±0.4%) |
| uniform_medium | Lazy | 3.21 ms (±2.1%) | 10.46 ms (±2.7%) | 7.95 ms (±2.8%) | 4.38 ms (±0.5%) |
| uniform_dense | Decrease-Key | 1.64 ms (±3.7%) | 15.72 ms (±1.7%) | 2.86 ms (±3.2%) | 2.06 ms (±1.9%) |
| uniform_dense | Lazy | 3.17 ms (±2.5%) | 9.10 ms (±2.7%) | 6.92 ms (±2.3%) | 3.72 ms (±2.0%) |
| grid_224 | Decrease-Key | 2.47 ms (±0.4%) | 12.28 ms (±0.8%) | 7.24 ms (±0.8%) | 3.10 ms (±0.4%) |
| grid_224 | Lazy | 2.81 ms (±1.0%) | 9.93 ms (±1.9%) | 9.05 ms (±0.6%) | 3.56 ms (±1.0%) |
| hub_skewed | Decrease-Key | 1.54 ms (±0.8%) | 6.56 ms (±5.0%) | 4.06 ms (±0.5%) | 2.14 ms (±1.6%) |
| hub_skewed | Lazy | 1.72 ms (±0.5%) | 5.65 ms (±1.2%) | 4.48 ms (±0.4%) | 2.30 ms (±0.4%) |
| layered_frontier | Decrease-Key | 1.17 ms (±0.6%) | 11.92 ms (±0.6%) | 3.70 ms (±0.6%) | 1.73 ms (±0.3%) |
| layered_frontier | Lazy | 2.33 ms (±0.3%) | 7.97 ms (±0.9%) | 6.74 ms (±0.4%) | 2.80 ms (±1.2%) |
