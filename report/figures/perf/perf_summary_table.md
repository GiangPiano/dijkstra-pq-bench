# Experiment 2: Microarchitectural Profiling (perf stat)

| Variant | Config | Mode | L1-D Miss (%) | LLC Miss (%) | Branch Miss (%) | IPC | Instructions | Cycles |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| binary | sparse | decrease_key | 26.56% | 50.00% | 2.37% | 0.82 | 217,359,110 | 264,264,826 |
| pairing | sparse | decrease_key | 24.29% | 42.89% | 2.27% | 0.88 | 250,679,028 | 285,162,916 |
| fibonacci | sparse | decrease_key | 18.90% | 39.65% | 4.49% | 1.02 | 357,508,616 | 349,845,802 |
| brodal-okasaki | sparse | decrease_key | 26.06% | 34.98% | 1.89% | 1.54 | 7,951,965,955 | 5,161,327,430 |
| binary | sparse | lazy | 25.64% | 47.58% | 2.34% | 0.91 | 237,873,832 | 260,586,644 |
| pairing | sparse | lazy | 23.40% | 38.44% | 2.09% | 0.94 | 277,735,780 | 296,807,372 |
| fibonacci | sparse | lazy | 17.30% | 33.86% | 4.46% | 1.09 | 420,642,251 | 384,876,670 |
| brodal-okasaki | sparse | lazy | 6.10% | 39.38% | 3.79% | 1.30 | 850,682,672 | 652,594,726 |
| binary | dense | decrease_key | 24.97% | 53.04% | 1.85% | 0.96 | 353,727,191 | 367,965,783 |
| pairing | dense | decrease_key | 23.99% | 39.49% | 1.82% | 0.94 | 392,592,852 | 418,773,238 |
| fibonacci | dense | decrease_key | 21.83% | 42.07% | 2.87% | 1.07 | 439,466,921 | 411,248,107 |
| brodal-okasaki | dense | decrease_key | N/A | N/A | N/A | N/A | N/A | N/A |
| binary | dense | lazy | 22.15% | 61.99% | 1.77% | 1.12 | 503,760,373 | 450,494,837 |
| pairing | dense | lazy | 20.60% | 39.37% | 1.47% | 1.04 | 601,011,275 | 577,998,222 |
| fibonacci | dense | lazy | 15.29% | 40.55% | 3.76% | 1.20 | 863,892,988 | 721,775,186 |
| brodal-okasaki | dense | lazy | 17.37% | 52.68% | 2.61% | 0.88 | 10,412,998,365 | 11,793,045,262 |
