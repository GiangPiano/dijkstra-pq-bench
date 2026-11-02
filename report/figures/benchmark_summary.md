# Dijkstra Priority Queue Benchmark Results

| Dataset | Mode | binary | brodal-okasaki | fibonacci | pairing |
|:---|:---| :---: | :---: | :---: | :---: |
| tiny_dense | Decrease-Key | 3.43 µs (±1.3%) | — | 3.54 µs (±1.7%) | 2.96 µs (±1.2%) |
| tiny_dense | Lazy | 5.39 µs (±1.1%) | — | 7.44 µs (±0.9%) | 4.90 µs (±0.8%) |
| small_med | Decrease-Key | 446.54 µs (±1.5%) | 8.77 ms (±0.6%) | 418.53 µs (±1.3%) | 228.62 µs (±1.6%) |
| small_med | Lazy | 803.46 µs (±1.0%) | 2.73 ms (±0.8%) | 855.96 µs (±2.4%) | 352.78 µs (±0.3%) |
| mod_sparse | Decrease-Key | 34.55 ms (±1.2%) | — | 39.06 ms (±1.8%) | 24.68 ms (±1.4%) |
| mod_sparse | Lazy | 41.46 ms (±2.1%) | — | 46.92 ms (±0.3%) | 29.46 ms (±1.5%) |
| big_sparse | Decrease-Key | 13.72 ms (±1.9%) | — | 40.59 ms (±0.7%) | 24.68 ms (±1.1%) |
| big_sparse | Lazy | 16.41 ms (±2.5%) | — | 50.24 ms (±1.2%) | 32.00 ms (±0.8%) |
