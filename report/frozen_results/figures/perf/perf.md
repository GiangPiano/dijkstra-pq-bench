# Experiment 2: Microarchitectural Profiling (perf stat)

Counts are per Dijkstra run; per-vertex columns divide by the graph's vertex count.

| Variant | Config | Mode | L1-D Miss (%) | LLC Miss (%) | Branch Miss (%) | IPC | Instructions | Cycles | Instr/vertex | L1 misses/vertex | Branch misses/vertex | LLC misses/vertex |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| binary | smoke_1k | decrease_key | 1.72% | 87.50% | 2.43% | 2.32 | 395,719 | 170,461 | 396 | 1.6 | 1.7 | 0 |
| brodal-okasaki | smoke_1k | decrease_key | 1.02% | 95.67% | 11.16% | 1.12 | 1,244,958 | 1,108,388 | 1.24k | 3.4 | 25 | 0.005 |
| fibonacci | smoke_1k | decrease_key | 1.59% | 90.48% | 4.57% | 1.81 | 1,258,004 | 693,443 | 1.26k | 4 | 14 | 0.001 |
| pairing | smoke_1k | decrease_key | 1.91% | 83.33% | 2.15% | 2.49 | 625,946 | 251,471 | 626 | 2.8 | 2.5 | 0.001 |
| binary | smoke_1k | lazy | 1.72% | 57.14% | 2.69% | 2.28 | 480,532 | 210,956 | 481 | 1.8 | 2.3 | 0 |
| brodal-okasaki | smoke_1k | lazy | 0.98% | 84.00% | 10.79% | 1.14 | 1,041,650 | 915,057 | 1.04k | 2.7 | 21 | 0 |
| fibonacci | smoke_1k | lazy | 1.65% | 91.95% | 4.55% | 1.84 | 1,622,551 | 881,388 | 1.62k | 5.2 | 18 | 0.002 |
| pairing | smoke_1k | lazy | 1.97% | 62.50% | 2.01% | 2.59 | 767,324 | 296,771 | 767 | 3.3 | 2.9 | 0 |
| binary | uniform_sparse | decrease_key | 9.14% | 86.79% | 4.94% | 1.45 | 4,936,273 | 3,412,150 | 494 | 9.9 | 4.2 | 0.0023 |
| brodal-okasaki | uniform_sparse | decrease_key | 3.98% | 77.14% | 11.35% | 1.03 | 16,967,604 | 16,439,380 | 1.7k | 18 | 34 | 0.018 |
| fibonacci | uniform_sparse | decrease_key | 4.93% | 77.23% | 5.67% | 1.53 | 14,310,134 | 9,376,855 | 1.43k | 14 | 19 | 0.007 |
| pairing | uniform_sparse | decrease_key | 8.46% | 84.06% | 4.03% | 1.62 | 7,307,217 | 4,499,363 | 731 | 14 | 5.2 | 0.0097 |
| binary | uniform_sparse | lazy | 9.57% | 79.10% | 4.38% | 1.48 | 6,087,800 | 4,124,698 | 609 | 12 | 4.6 | 0.008 |
| brodal-okasaki | uniform_sparse | lazy | 4.39% | 68.06% | 11.07% | 1.05 | 14,021,799 | 13,410,778 | 1.4k | 16 | 28 | 0.015 |
| fibonacci | uniform_sparse | lazy | 4.84% | 57.21% | 5.42% | 1.58 | 18,232,596 | 11,528,854 | 1.82k | 17 | 23 | 0.012 |
| pairing | uniform_sparse | lazy | 8.64% | 57.79% | 3.45% | 1.71 | 9,010,049 | 5,270,599 | 901 | 17 | 5.4 | 0.0058 |
| binary | uniform_medium | decrease_key | 12.46% | 1.27% | 5.12% | 1.30 | 13,304,566 | 10,247,957 | 665 | 19 | 5.8 | 0.019 |
| brodal-okasaki | uniform_medium | decrease_key | 4.72% | 5.73% | 10.58% | 0.94 | 71,935,952 | 76,355,404 | 3.6k | 45 | 67 | 0.3 |
| fibonacci | uniform_medium | decrease_key | 6.92% | 0.75% | 5.75% | 1.41 | 32,661,341 | 23,160,873 | 1.63k | 24 | 22 | 0.024 |
| pairing | uniform_medium | decrease_key | 10.86% | 0.80% | 4.04% | 1.31 | 19,183,859 | 14,595,959 | 959 | 24 | 6.9 | 0.024 |
| binary | uniform_medium | lazy | 10.44% | 1.31% | 3.94% | 1.39 | 21,725,925 | 15,587,722 | 1.09k | 23 | 7.3 | 0.029 |
| brodal-okasaki | uniform_medium | lazy | 5.23% | 4.78% | 10.13% | 0.99 | 50,105,512 | 50,562,916 | 2.51k | 35 | 45 | 0.17 |
| fibonacci | uniform_medium | lazy | 5.30% | 3.99% | 5.10% | 1.51 | 59,086,682 | 39,242,491 | 2.95k | 31 | 35 | 0.19 |
| pairing | uniform_medium | lazy | 9.29% | 4.12% | 2.82% | 1.33 | 31,177,870 | 23,385,796 | 1.56k | 31 | 7.8 | 0.17 |
| binary | uniform_dense | decrease_key | 11.04% | 5.14% | 3.93% | 1.52 | 11,956,266 | 7,859,519 | 1.2k | 36 | 7.9 | 0.12 |
| brodal-okasaki | uniform_dense | decrease_key | 4.90% | 12.79% | 10.04% | 0.96 | 72,994,718 | 76,391,247 | 7.3k | 97 | 129 | 1.2 |
| fibonacci | uniform_dense | decrease_key | 8.61% | 4.55% | 4.86% | 1.49 | 20,965,921 | 14,070,628 | 2.1k | 44 | 22 | 0.18 |
| pairing | uniform_dense | decrease_key | 10.98% | 2.73% | 3.38% | 1.54 | 15,788,525 | 10,246,610 | 1.58k | 46 | 9.6 | 0.091 |
| binary | uniform_dense | lazy | 9.29% | 9.02% | 3.05% | 1.54 | 22,010,023 | 14,255,732 | 2.2k | 43 | 12 | 0.26 |
| brodal-okasaki | uniform_dense | lazy | 5.32% | 11.60% | 9.23% | 1.04 | 45,741,248 | 43,994,226 | 4.57k | 65 | 76 | 0.55 |
| fibonacci | uniform_dense | lazy | 5.42% | 12.15% | 4.65% | 1.58 | 53,367,047 | 33,778,735 | 5.34k | 59 | 57 | 0.66 |
| pairing | uniform_dense | lazy | 8.91% | 5.31% | 2.21% | 1.67 | 30,597,203 | 18,363,614 | 3.06k | 61 | 12 | 0.25 |
| binary | grid_224 | decrease_key | 3.45% | 4.13% | 4.26% | 1.62 | 20,479,806 | 12,627,763 | 408 | 3.3 | 3 | 0.0012 |
| brodal-okasaki | grid_224 | decrease_key | 1.41% | 34.92% | 10.91% | 1.11 | 66,271,796 | 59,971,702 | 1.32k | 5 | 26 | 0.02 |
| fibonacci | grid_224 | decrease_key | 1.86% | 17.24% | 4.55% | 1.74 | 61,731,381 | 35,501,497 | 1.23k | 4.6 | 13 | 0.0087 |
| pairing | grid_224 | decrease_key | 3.09% | 4.80% | 3.95% | 1.87 | 28,030,449 | 14,982,590 | 559 | 4.1 | 3.8 | 0.002 |
| binary | grid_224 | lazy | 3.40% | 3.71% | 3.79% | 1.83 | 24,871,596 | 13,582,676 | 496 | 3.6 | 3.3 | 0.0011 |
| brodal-okasaki | grid_224 | lazy | 1.45% | 25.92% | 10.19% | 1.16 | 55,027,311 | 47,584,086 | 1.1k | 4.2 | 20 | 0.014 |
| fibonacci | grid_224 | lazy | 1.84% | 19.02% | 4.30% | 1.83 | 79,949,838 | 43,697,578 | 1.59k | 5.6 | 16 | 0.01 |
| pairing | grid_224 | lazy | 3.11% | 5.28% | 3.42% | 2.05 | 34,598,644 | 16,911,088 | 690 | 4.8 | 4 | 0.0025 |
| binary | hub_skewed | decrease_key | 7.44% | 0.90% | 3.55% | 1.56 | 11,667,317 | 7,484,917 | 583 | 9.5 | 3.5 | 0.0051 |
| brodal-okasaki | hub_skewed | decrease_key | 3.79% | 2.06% | 10.00% | 1.05 | 32,377,197 | 30,912,784 | 1.62k | 17 | 29 | 0.036 |
| fibonacci | hub_skewed | decrease_key | 4.29% | 0.47% | 5.05% | 1.62 | 32,247,716 | 19,934,535 | 1.61k | 14 | 19 | 0.011 |
| pairing | hub_skewed | decrease_key | 6.75% | 0.32% | 2.22% | 1.77 | 18,375,732 | 10,381,882 | 919 | 14 | 3.7 | 0.006 |
| binary | hub_skewed | lazy | 8.25% | 1.16% | 3.56% | 1.54 | 12,881,786 | 8,373,944 | 644 | 11 | 4 | 0.0077 |
| brodal-okasaki | hub_skewed | lazy | 4.19% | 2.35% | 9.97% | 1.05 | 28,575,242 | 27,186,040 | 1.43k | 16 | 26 | 0.035 |
| fibonacci | hub_skewed | lazy | 4.34% | 0.74% | 5.05% | 1.63 | 36,072,216 | 22,084,370 | 1.8k | 16 | 21 | 0.018 |
| pairing | hub_skewed | lazy | 7.40% | 0.32% | 2.25% | 1.75 | 19,786,397 | 11,319,605 | 989 | 16 | 4.1 | 0.0063 |
| binary | layered_frontier | decrease_key | 4.04% | 0.93% | 3.46% | 1.93 | 10,789,370 | 5,595,597 | 539 | 5.1 | 3.2 | 0.0011 |
| brodal-okasaki | layered_frontier | decrease_key | 3.24% | 35.63% | 11.28% | 1.05 | 61,056,227 | 58,353,805 | 3.05k | 26 | 61 | 0.075 |
| fibonacci | layered_frontier | decrease_key | 3.61% | 6.19% | 5.72% | 1.55 | 27,921,218 | 18,049,228 | 1.4k | 11 | 19 | 0.011 |
| pairing | layered_frontier | decrease_key | 5.11% | 2.02% | 3.64% | 1.82 | 15,189,696 | 8,344,310 | 759 | 9.3 | 4.9 | 0.0033 |
| binary | layered_frontier | lazy | 5.69% | 2.62% | 3.67% | 1.64 | 18,392,315 | 11,188,995 | 920 | 11 | 5.8 | 0.0036 |
| brodal-okasaki | layered_frontier | lazy | 3.09% | 26.41% | 10.78% | 1.07 | 41,875,192 | 38,975,467 | 2.09k | 17 | 41 | 0.033 |
| fibonacci | layered_frontier | lazy | 3.71% | 16.12% | 5.24% | 1.62 | 53,018,819 | 32,677,466 | 2.65k | 19 | 32 | 0.031 |
| pairing | layered_frontier | lazy | 6.31% | 5.27% | 3.14% | 1.85 | 25,025,721 | 13,516,089 | 1.25k | 17 | 6.7 | 0.0089 |
