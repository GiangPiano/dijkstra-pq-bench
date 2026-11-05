# Experiment 2: Microarchitectural Profiling (perf stat)

Counts are per Dijkstra run; per-vertex columns divide by the graph's vertex count.

| Variant | Config | Mode | L1-D Miss (%) | LLC Miss (%) | Branch Miss (%) | IPC | Instructions | Cycles | Instr/vertex | L1 misses/vertex | Branch misses/vertex | LLC misses/vertex |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| binary | smoke_1k | decrease_key | 1.72% | 40.00% | 2.44% | 2.43 | 395,719 | 163,083 | 396 | 1.6 | 1.7 | 0 |
| brodal-okasaki | smoke_1k | decrease_key | 1.00% | 96.97% | 11.38% | 1.11 | 1,244,958 | 1,117,669 | 1.24k | 3.4 | 26 | 0.002 |
| fibonacci | smoke_1k | decrease_key | 1.59% | 86.84% | 4.56% | 1.82 | 1,258,004 | 689,831 | 1.26k | 4 | 14 | 0.001 |
| pairing | smoke_1k | decrease_key | 1.90% | 52.94% | 2.13% | 2.57 | 625,946 | 243,736 | 626 | 2.8 | 2.5 | 0 |
| binary | smoke_1k | lazy | 1.70% | 70.59% | 2.62% | 2.16 | 480,532 | 222,430 | 481 | 1.7 | 2.2 | 0 |
| brodal-okasaki | smoke_1k | lazy | 0.99% | 95.93% | 10.73% | 1.13 | 1,041,635 | 918,187 | 1.04k | 2.7 | 20 | 0.002 |
| fibonacci | smoke_1k | lazy | 1.62% | 82.35% | 4.56% | 1.84 | 1,622,551 | 881,143 | 1.62k | 5.1 | 18 | 0.001 |
| pairing | smoke_1k | lazy | 1.96% | 66.67% | 2.02% | 2.59 | 767,323 | 296,539 | 767 | 3.3 | 2.9 | 0 |
| binary | uniform_sparse | decrease_key | 9.15% | 12.23% | 4.90% | 1.45 | 4,936,273 | 3,406,813 | 494 | 9.9 | 4.2 | 0.0023 |
| brodal-okasaki | uniform_sparse | decrease_key | 3.98% | 7.79% | 11.34% | 1.03 | 16,967,604 | 16,502,458 | 1.7k | 18 | 34 | 0.01 |
| fibonacci | uniform_sparse | decrease_key | 4.93% | 40.67% | 5.64% | 1.54 | 14,378,594 | 9,356,846 | 1.44k | 14 | 19 | 0.006 |
| pairing | uniform_sparse | decrease_key | 8.44% | 19.14% | 4.02% | 1.63 | 7,307,217 | 4,488,254 | 731 | 14 | 5.2 | 0.0037 |
| binary | uniform_sparse | lazy | 9.57% | 58.19% | 4.39% | 1.47 | 6,087,800 | 4,129,798 | 609 | 12 | 4.6 | 0.0021 |
| brodal-okasaki | uniform_sparse | lazy | 4.40% | 39.51% | 11.06% | 1.04 | 14,021,784 | 13,422,533 | 1.4k | 16 | 28 | 0.013 |
| fibonacci | uniform_sparse | lazy | 4.84% | 31.47% | 5.37% | 1.59 | 18,322,336 | 11,511,198 | 1.83k | 17 | 23 | 0.01 |
| pairing | uniform_sparse | lazy | 8.64% | 36.90% | 3.46% | 1.70 | 9,010,064 | 5,299,479 | 901 | 17 | 5.5 | 0.0076 |
| binary | uniform_medium | decrease_key | 12.45% | 0.97% | 5.12% | 1.30 | 13,304,554 | 10,264,244 | 665 | 19 | 5.8 | 0.014 |
| brodal-okasaki | uniform_medium | decrease_key | 4.78% | 8.70% | 10.57% | 0.94 | 71,935,953 | 76,919,143 | 3.6k | 46 | 67 | 0.5 |
| fibonacci | uniform_medium | decrease_key | 6.93% | 2.31% | 5.78% | 1.38 | 32,521,363 | 23,519,145 | 1.63k | 24 | 22 | 0.072 |
| pairing | uniform_medium | decrease_key | 10.60% | 1.04% | 4.04% | 1.33 | 19,183,859 | 14,474,244 | 959 | 24 | 6.9 | 0.026 |
| binary | uniform_medium | lazy | 10.44% | 2.43% | 3.93% | 1.39 | 21,725,925 | 15,655,718 | 1.09k | 23 | 7.3 | 0.055 |
| brodal-okasaki | uniform_medium | lazy | 5.22% | 6.17% | 10.12% | 0.99 | 50,105,512 | 50,629,652 | 2.51k | 35 | 45 | 0.21 |
| fibonacci | uniform_medium | lazy | 5.37% | 3.97% | 5.08% | 1.51 | 59,357,834 | 39,201,129 | 2.97k | 31 | 35 | 0.2 |
| pairing | uniform_medium | lazy | 9.13% | 1.99% | 2.82% | 1.42 | 31,177,870 | 21,904,885 | 1.56k | 31 | 7.8 | 0.075 |
| binary | uniform_dense | decrease_key | 11.04% | 7.59% | 3.91% | 1.45 | 11,956,267 | 8,225,358 | 1.2k | 36 | 7.9 | 0.17 |
| brodal-okasaki | uniform_dense | decrease_key | 4.87% | 14.01% | 10.04% | 0.96 | 72,994,716 | 76,184,242 | 7.3k | 96 | 129 | 1.2 |
| fibonacci | uniform_dense | decrease_key | 8.61% | 4.47% | 4.87% | 1.47 | 20,895,935 | 14,187,152 | 2.09k | 44 | 22 | 0.18 |
| pairing | uniform_dense | decrease_key | 10.98% | 2.91% | 3.39% | 1.52 | 15,788,525 | 10,386,754 | 1.58k | 46 | 9.6 | 0.097 |
| binary | uniform_dense | lazy | 9.28% | 5.11% | 3.05% | 1.58 | 22,010,023 | 13,929,613 | 2.2k | 43 | 12 | 0.15 |
| brodal-okasaki | uniform_dense | lazy | 5.32% | 10.99% | 9.21% | 1.04 | 45,741,247 | 44,121,275 | 4.57k | 65 | 76 | 0.52 |
| fibonacci | uniform_dense | lazy | 5.43% | 9.50% | 4.65% | 1.60 | 53,367,047 | 33,341,259 | 5.34k | 59 | 57 | 0.52 |
| pairing | uniform_dense | lazy | 9.08% | 14.75% | 2.22% | 1.49 | 30,597,203 | 20,494,547 | 3.06k | 62 | 12 | 0.74 |
| binary | grid_224 | decrease_key | 3.54% | 3.40% | 4.25% | 1.73 | 20,479,806 | 11,825,030 | 408 | 3.4 | 3 | 0.00098 |
| brodal-okasaki | grid_224 | decrease_key | 1.40% | 33.99% | 10.92% | 1.11 | 66,271,794 | 59,621,672 | 1.32k | 5 | 26 | 0.02 |
| fibonacci | grid_224 | decrease_key | 1.87% | 18.34% | 4.55% | 1.74 | 61,731,381 | 35,512,902 | 1.23k | 4.6 | 13 | 0.0092 |
| pairing | grid_224 | decrease_key | 3.15% | 6.42% | 3.95% | 1.84 | 28,030,450 | 15,216,005 | 559 | 4.2 | 3.8 | 0.0025 |
| binary | grid_224 | lazy | 3.28% | 9.27% | 3.81% | 1.83 | 24,871,596 | 13,605,624 | 496 | 3.4 | 3.3 | 0.003 |
| brodal-okasaki | grid_224 | lazy | 1.44% | 29.08% | 10.18% | 1.16 | 55,027,311 | 47,600,802 | 1.1k | 4.2 | 20 | 0.016 |
| fibonacci | grid_224 | lazy | 1.88% | 25.53% | 4.30% | 1.81 | 79,949,838 | 44,091,543 | 1.59k | 5.8 | 16 | 0.014 |
| pairing | grid_224 | lazy | 3.11% | 4.70% | 3.42% | 2.05 | 34,598,644 | 16,905,740 | 690 | 4.8 | 4.1 | 0.0022 |
| binary | hub_skewed | decrease_key | 7.41% | 0.73% | 3.54% | 1.55 | 11,667,317 | 7,534,332 | 583 | 9.4 | 3.5 | 0.0044 |
| brodal-okasaki | hub_skewed | decrease_key | 3.79% | 1.65% | 10.01% | 1.05 | 32,377,197 | 30,931,756 | 1.62k | 17 | 29 | 0.027 |
| fibonacci | hub_skewed | decrease_key | 4.28% | 0.52% | 5.06% | 1.61 | 32,247,716 | 20,003,290 | 1.61k | 14 | 19 | 0.012 |
| pairing | hub_skewed | decrease_key | 6.76% | 0.19% | 2.22% | 1.78 | 18,375,731 | 10,349,344 | 919 | 14 | 3.7 | 0.0033 |
| binary | hub_skewed | lazy | 8.25% | 0.85% | 3.56% | 1.54 | 12,881,786 | 8,389,262 | 644 | 11 | 4 | 0.0053 |
| brodal-okasaki | hub_skewed | lazy | 4.19% | 1.46% | 9.98% | 1.06 | 28,575,257 | 27,070,423 | 1.43k | 16 | 26 | 0.02 |
| fibonacci | hub_skewed | lazy | 4.34% | 0.76% | 5.03% | 1.62 | 36,235,827 | 22,339,841 | 1.81k | 16 | 21 | 0.019 |
| pairing | hub_skewed | lazy | 7.40% | 0.29% | 2.26% | 1.75 | 19,786,397 | 11,317,443 | 989 | 16 | 4.1 | 0.0055 |
| binary | layered_frontier | decrease_key | 4.04% | 0.82% | 3.46% | 1.93 | 10,789,369 | 5,583,863 | 539 | 5.1 | 3.2 | 0.001 |
| brodal-okasaki | layered_frontier | decrease_key | 3.24% | 32.91% | 11.28% | 1.05 | 61,056,226 | 58,246,670 | 3.05k | 26 | 61 | 0.068 |
| fibonacci | layered_frontier | decrease_key | 3.60% | 6.14% | 5.74% | 1.55 | 27,784,936 | 17,925,999 | 1.39k | 11 | 19 | 0.01 |
| pairing | layered_frontier | decrease_key | 5.10% | 1.62% | 3.65% | 1.82 | 15,189,696 | 8,323,778 | 759 | 9.2 | 4.9 | 0.0026 |
| binary | layered_frontier | lazy | 5.69% | 3.59% | 3.67% | 1.63 | 18,392,315 | 11,278,252 | 920 | 11 | 5.8 | 0.005 |
| brodal-okasaki | layered_frontier | lazy | 3.17% | 25.64% | 10.78% | 1.06 | 41,875,193 | 39,360,303 | 2.09k | 18 | 41 | 0.047 |
| fibonacci | layered_frontier | lazy | 3.72% | 17.00% | 5.28% | 1.60 | 52,743,845 | 32,881,187 | 2.64k | 19 | 32 | 0.033 |
| pairing | layered_frontier | lazy | 6.22% | 2.96% | 3.14% | 1.87 | 25,025,721 | 13,395,956 | 1.25k | 17 | 6.7 | 0.0046 |
