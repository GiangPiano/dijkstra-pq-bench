# Experiment 2: Microarchitectural Profiling (perf stat)

Counts are per Dijkstra run; per-vertex columns divide by the graph's vertex count.

| Variant | Config | Mode | L1-D Miss (%) | LLC Miss (%) | Branch Miss (%) | IPC | Instructions | Cycles | Instr/vertex | L1 misses/vertex | Branch misses/vertex | LLC misses/vertex |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| binary | smoke_1k | decrease_key | 1.71% | 50.00% | 2.49% | 2.41 | 395,719 | 164,217 | 396 | 1.6 | 1.7 | 0 |
| brodal-okasaki | smoke_1k | decrease_key | 0.99% | 68.42% | 11.71% | 1.10 | 1,244,958 | 1,136,056 | 1.24k | 3.3 | 26 | 0 |
| fibonacci | smoke_1k | decrease_key | 1.55% | 57.14% | 4.55% | 1.82 | 1,258,004 | 690,225 | 1.26k | 3.9 | 14 | 0 |
| pairing | smoke_1k | decrease_key | 1.90% | 61.11% | 2.12% | 2.53 | 625,946 | 247,692 | 626 | 2.8 | 2.5 | 0 |
| binary | smoke_1k | lazy | 1.72% | 75.00% | 2.60% | 2.23 | 480,532 | 215,103 | 481 | 1.8 | 2.2 | 0 |
| brodal-okasaki | smoke_1k | lazy | 0.98% | 63.64% | 11.04% | 1.12 | 1,041,636 | 929,464 | 1.04k | 2.7 | 21 | 0 |
| fibonacci | smoke_1k | lazy | 1.60% | 70.00% | 4.49% | 1.86 | 1,631,462 | 877,729 | 1.63k | 5.1 | 17 | 0 |
| pairing | smoke_1k | lazy | 1.98% | 81.97% | 2.05% | 2.41 | 767,323 | 318,659 | 767 | 3.4 | 2.9 | 0.001 |
| binary | uniform_sparse | decrease_key | 9.15% | 89.80% | 4.91% | 1.44 | 4,936,273 | 3,436,525 | 494 | 9.9 | 4.2 | 0.0047 |
| brodal-okasaki | uniform_sparse | decrease_key | 3.98% | 58.81% | 11.35% | 1.03 | 16,967,609 | 16,443,637 | 1.7k | 18 | 34 | 0.0087 |
| fibonacci | uniform_sparse | decrease_key | 4.92% | 48.42% | 5.68% | 1.52 | 14,310,136 | 9,384,373 | 1.43k | 14 | 19 | 0.0029 |
| pairing | uniform_sparse | decrease_key | 8.43% | 65.03% | 4.02% | 1.63 | 7,307,217 | 4,485,078 | 731 | 14 | 5.2 | 0.0038 |
| binary | uniform_sparse | lazy | 9.57% | 76.54% | 4.35% | 1.49 | 6,087,798 | 4,096,378 | 609 | 12 | 4.6 | 0.0014 |
| brodal-okasaki | uniform_sparse | lazy | 4.39% | 65.23% | 11.07% | 1.05 | 14,021,787 | 13,407,739 | 1.4k | 16 | 28 | 0.01 |
| fibonacci | uniform_sparse | lazy | 4.83% | 33.97% | 5.39% | 1.57 | 18,232,600 | 11,612,334 | 1.82k | 17 | 23 | 0.015 |
| pairing | uniform_sparse | lazy | 8.67% | 15.69% | 3.42% | 1.71 | 9,010,049 | 5,280,019 | 901 | 17 | 5.4 | 0.0042 |
| binary | uniform_medium | decrease_key | 12.83% | 0.69% | 5.13% | 1.28 | 13,304,567 | 10,414,668 | 665 | 20 | 5.8 | 0.013 |
| brodal-okasaki | uniform_medium | decrease_key | 4.77% | 2.33% | 10.58% | 0.94 | 71,935,964 | 76,447,767 | 3.6k | 46 | 67 | 0.14 |
| fibonacci | uniform_medium | decrease_key | 7.06% | 0.85% | 5.75% | 1.39 | 32,661,349 | 23,521,559 | 1.63k | 24 | 22 | 0.03 |
| pairing | uniform_medium | decrease_key | 10.63% | 0.86% | 4.04% | 1.35 | 19,183,864 | 14,237,496 | 959 | 24 | 6.9 | 0.022 |
| binary | uniform_medium | lazy | 10.46% | 1.82% | 3.94% | 1.41 | 21,725,944 | 15,439,694 | 1.09k | 23 | 7.3 | 0.041 |
| brodal-okasaki | uniform_medium | lazy | 5.16% | 5.16% | 10.11% | 1.01 | 50,105,527 | 49,713,533 | 2.51k | 34 | 45 | 0.16 |
| fibonacci | uniform_medium | lazy | 5.38% | 4.46% | 5.06% | 1.48 | 59,357,847 | 40,200,688 | 2.97k | 31 | 35 | 0.22 |
| pairing | uniform_medium | lazy | 9.14% | 2.27% | 2.82% | 1.46 | 31,177,877 | 21,372,270 | 1.56k | 31 | 7.8 | 0.085 |
| binary | uniform_dense | decrease_key | 11.00% | 2.09% | 3.92% | 1.52 | 11,956,267 | 7,860,343 | 1.2k | 36 | 7.9 | 0.046 |
| brodal-okasaki | uniform_dense | decrease_key | 4.90% | 8.22% | 10.04% | 0.95 | 72,994,736 | 76,818,359 | 7.3k | 97 | 129 | 0.72 |
| fibonacci | uniform_dense | decrease_key | 8.59% | 1.02% | 4.86% | 1.50 | 20,895,934 | 13,884,551 | 2.09k | 44 | 22 | 0.041 |
| pairing | uniform_dense | decrease_key | 10.98% | 0.75% | 3.38% | 1.56 | 15,788,524 | 10,094,852 | 1.58k | 46 | 9.6 | 0.025 |
| binary | uniform_dense | lazy | 9.27% | 8.19% | 3.04% | 1.50 | 22,010,022 | 14,706,182 | 2.2k | 43 | 12 | 0.24 |
| brodal-okasaki | uniform_dense | lazy | 5.31% | 8.25% | 9.22% | 1.03 | 45,741,253 | 44,447,167 | 4.57k | 65 | 76 | 0.39 |
| fibonacci | uniform_dense | lazy | 5.41% | 7.63% | 4.65% | 1.58 | 53,367,064 | 33,846,940 | 5.34k | 59 | 57 | 0.41 |
| pairing | uniform_dense | lazy | 8.91% | 1.95% | 2.21% | 1.67 | 30,597,201 | 18,313,444 | 3.06k | 61 | 12 | 0.091 |
| binary | grid_224 | decrease_key | 3.57% | 0.95% | 4.26% | 1.74 | 20,479,809 | 11,783,205 | 408 | 3.4 | 3 | 0.00022 |
| brodal-okasaki | grid_224 | decrease_key | 1.36% | 12.24% | 10.91% | 1.12 | 66,271,806 | 59,149,403 | 1.32k | 4.8 | 26 | 0.0065 |
| fibonacci | grid_224 | decrease_key | 1.84% | 5.15% | 4.54% | 1.75 | 61,731,389 | 35,212,486 | 1.23k | 4.5 | 13 | 0.0024 |
| pairing | grid_224 | decrease_key | 3.14% | 0.92% | 3.96% | 1.83 | 28,030,468 | 15,275,914 | 559 | 4.2 | 3.8 | 0.00036 |
| binary | grid_224 | lazy | 3.27% | 0.25% | 3.78% | 1.85 | 24,871,597 | 13,426,326 | 496 | 3.4 | 3.3 | 8e-05 |
| brodal-okasaki | grid_224 | lazy | 1.45% | 25.46% | 10.22% | 1.15 | 55,027,323 | 47,910,777 | 1.1k | 4.2 | 20 | 0.014 |
| fibonacci | grid_224 | lazy | 1.88% | 58.77% | 4.28% | 1.79 | 80,413,189 | 44,815,964 | 1.6k | 5.8 | 16 | 0.039 |
| pairing | grid_224 | lazy | 3.14% | 15.05% | 3.42% | 2.03 | 34,598,650 | 17,070,014 | 690 | 4.8 | 4 | 0.0073 |
| binary | hub_skewed | decrease_key | 7.44% | 1.48% | 3.54% | 1.55 | 11,667,320 | 7,521,968 | 583 | 9.5 | 3.5 | 0.0095 |
| brodal-okasaki | hub_skewed | decrease_key | 3.79% | 2.19% | 9.99% | 1.06 | 32,377,208 | 30,592,383 | 1.62k | 17 | 29 | 0.034 |
| fibonacci | hub_skewed | decrease_key | 4.27% | 0.44% | 5.06% | 1.63 | 32,247,722 | 19,765,969 | 1.61k | 14 | 19 | 0.0099 |
| pairing | hub_skewed | decrease_key | 6.76% | 0.37% | 2.22% | 1.76 | 18,375,745 | 10,416,410 | 919 | 14 | 3.7 | 0.0066 |
| binary | hub_skewed | lazy | 8.24% | 0.79% | 3.56% | 1.53 | 12,881,786 | 8,434,209 | 644 | 11 | 4 | 0.0051 |
| brodal-okasaki | hub_skewed | lazy | 4.18% | 0.64% | 9.97% | 1.06 | 28,575,248 | 27,007,631 | 1.43k | 16 | 26 | 0.0078 |
| fibonacci | hub_skewed | lazy | 4.34% | 0.14% | 5.07% | 1.64 | 36,072,222 | 22,049,368 | 1.8k | 15 | 21 | 0.0031 |
| pairing | hub_skewed | lazy | 7.39% | 0.21% | 2.26% | 1.73 | 19,786,395 | 11,416,730 | 989 | 16 | 4.1 | 0.0037 |
| binary | layered_frontier | decrease_key | 4.04% | 0.21% | 3.45% | 1.91 | 10,789,370 | 5,660,559 | 539 | 5.1 | 3.2 | 0.00025 |
| brodal-okasaki | layered_frontier | decrease_key | 3.23% | 18.53% | 11.28% | 1.05 | 61,056,237 | 58,048,361 | 3.05k | 26 | 61 | 0.034 |
| fibonacci | layered_frontier | decrease_key | 3.57% | 2.81% | 5.72% | 1.56 | 27,921,222 | 17,954,101 | 1.4k | 10 | 19 | 0.0045 |
| pairing | layered_frontier | decrease_key | 5.08% | 0.37% | 3.63% | 1.82 | 15,189,696 | 8,325,962 | 759 | 9.2 | 4.8 | 0.00055 |
| binary | layered_frontier | lazy | 5.68% | 0.95% | 3.66% | 1.65 | 18,392,317 | 11,156,726 | 920 | 11 | 5.8 | 0.0013 |
| brodal-okasaki | layered_frontier | lazy | 3.08% | 4.11% | 10.78% | 1.08 | 41,875,202 | 38,674,316 | 2.09k | 17 | 41 | 0.0046 |
| fibonacci | layered_frontier | lazy | 3.64% | 3.23% | 5.27% | 1.62 | 52,743,852 | 32,473,247 | 2.64k | 19 | 32 | 0.0047 |
| pairing | layered_frontier | lazy | 6.31% | 3.37% | 3.15% | 1.82 | 25,025,725 | 13,772,001 | 1.25k | 17 | 6.7 | 0.0056 |
