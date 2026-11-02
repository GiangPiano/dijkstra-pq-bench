# Experiment 3: Memory Footprint & Allocator Pressure

| Variant | Config | Mode | Peak Heap (KiB) | Peak RSS (MiB) | Malloc Calls | Free Calls | Total Alloc (KiB) | Bytes/Vertex |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| binary | sparse | decrease_key | 1,171.9 | 255.4 | 3 | 3 | 1,171.9 | 24.0 |
| pairing | sparse | decrease_key | 1,180.8 | 256.5 | 49,058 | 49,058 | 2,306.9 | 24.2 |
| fibonacci | sparse | decrease_key | 1,497.4 | 256.8 | 49,058 | 49,058 | 3,073.4 | 30.7 |
| brodal-okasaki | sparse | decrease_key | 948.5 | 256.5 | 49,055 | 49,055 | 2,299.4 | 19.4 |
| binary | sparse | lazy | 1,171.9 | 255.4 | 3 | 3 | 1,171.9 | 24.0 |
| pairing | sparse | lazy | 1,456.5 | 257.0 | 64,442 | 64,442 | 2,907.8 | 29.8 |
| fibonacci | sparse | lazy | 1,883.9 | 257.4 | 64,469 | 64,469 | 3,916.2 | 38.6 |
| brodal-okasaki | sparse | lazy | 1,279.1 | 257.0 | 64,437 | 64,437 | 3,020.5 | 26.2 |
| binary | dense | decrease_key | 1,171.9 | 255.8 | 3 | 3 | 1,171.9 | 24.0 |
| pairing | dense | decrease_key | 2,255.0 | 258.2 | 50,002 | 50,002 | 2,343.8 | 46.2 |
| fibonacci | dense | decrease_key | 3,000.7 | 258.8 | 50,002 | 50,002 | 3,125.0 | 61.5 |
| brodal-okasaki | dense | decrease_key | N/A | N/A | N/A | N/A | N/A | N/A |
| binary | dense | lazy | 5,468.8 | 259.2 | 7 | 7 | 8,203.2 | 112.0 |
| pairing | dense | lazy | 6,987.5 | 265.6 | 196,939 | 196,939 | 8,083.5 | 143.1 |
| fibonacci | dense | lazy | 9,637.8 | 268.2 | 197,157 | 197,157 | 11,172.6 | 197.4 |
| brodal-okasaki | dense | lazy | 7,932.2 | 268.1 | 197,326 | 197,326 | 9,249.6 | 162.5 |
