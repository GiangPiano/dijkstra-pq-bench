# Plan for the Report 
> **NOTE:** The total word count should be 4000-6000 words
## 1. Introduction (500-600 words)
### 1.1. The problem
What is the problem that our Dijkstra is solving here? In a sense briefly mention how our input are formulate.

### 1.2. Dijkstra 
Briefly lay out the Dijkstra algorithm, maybe provide pseudocode. Mention its bottleneck, focus on the priority queue.

### 1.3. Brief intro of our heaps
- Structural definition, node layout, and memory representation for each heap.
- Primary author attributions clearly marked per implementation.

## 2. Theoretical Comparison and Pre-Experimental Predictions (~750-900 words)
* **Asymptotic complexity matrix:**
    * Comparative table detailing worst-case vs amortized bounds for `insert`, `extract-min`, and `decrease-key`, alongside pointer overhead per node.


* **Architectural & hardware considerations (on paper):**
    * Pointer chasing vs contiguous memory layouts (L1/L2/L3 cache misses).
    * Handle management: how each heap tracks node locations inside Dijkstra’s visitor state (external handles vs array indexing).


* **Pre-registered predictions:**
    * *Prediction 1 (Sparse vs Dense crossover):* Binary/$d$-ary heaps will dominate sparse graphs ($\vert{}E\vert{} \approx 2\vert{}V\vert{}$ to $4\vert{}V\vert{}$); pointer heaps will only catch up once average degree $\bar{d} \gg 32$ where `decrease-key` calls dominate.
    * *Prediction 2 (The Fibonacci barrier):* Fibonacci heap will fail to beat Pairing and 4-ary heaps at any practical graph size ($\vert{}V\vert{} \le 10^7$) due to cascading cut overhead and pointer indirection.
    * *Prediction 3 (Domain-specific wins):* The monotonic/integer heap (e.g., Radix) will outpace all comparison-based heaps when edge weights fall within a bounded integer range.



## 3. Experimental Methodology (~800–1,000 words)

* **Benchmarking testbed & hygiene:**
* Hardware specs (CPU, L1/L2/L3 cache sizes, RAM, OS), compiler versions, optimization flags (`-O3`, `-march=native`), and allocation strategies (e.g., arena allocation vs standard `malloc` to isolate pointer chasing from allocator jitter).
* Monotonic clock selection, warmup runs, iteration counts, and variance/interquartile range reporting.


* **Separation of concerns:**
* Pre-loading graph representations into memory (CSR / Adjacency list) to ensure I/O and graph parsing are completely excluded from heap runtime timers.


* **Input families & workload topology:**
* *Erdős–Rényi random graphs:* Parametric variation of edge density $p$ to isolate the exact degree ratio $\vert{}E\vert{}/\vert{}V\vert{}$ where `decrease-key` frequency flips runtime.
* *Grid / Mesh graphs:* High diameter, low degree ($\le 4$), deep priority queues with high extraction volume.
* *Real-world networks:* OpenStreetMap road networks (sparse, bounded planar degree) vs web graphs / social graphs (scale-free power-law degree distributions).
* *Adversarial / Degenerate inputs:* Graphs structured specifically to trigger frequent cascading cuts in Fibonacci or deep tree restructuring in Pairing.



## 4. Results and Structural Analysis (~1,200–1,500 words)

* **Empirical scaling curves & plots:**
* Wall-clock runtime vs $\vert{}V\vert{}$ (fixed density).
* Wall-clock runtime vs degree $\vert{}E\vert{}/\vert{}V\vert{}$ (isolating the `decrease-key` inflection point).
* Operation breakdown: cumulative time spent in `extract-min` vs `decrease-key`.


* **Hardware performance counters (perf / PAPI):**
* L1-D cache miss rates and branch mispredictions per heap type.
* Demonstrating empirically why contiguous array structures outpace pointer-heavy Fibonacci structures even when executing $2\times$ more comparisons.


* **Mechanistic analysis:**
* Explain *why* Pairing heap behaves like an aggressive practical approximation of Fibonacci without the structural bookkeeping overhead.
* Explain the performance impact of implicit node indices in $d$-ary heaps versus maintaining exterior node pointers.



## 5. What Surprised Us (~600–800 words)

* *Expectation vs Reality breakdown:*
* Example candidate surprise: Finding that explicit `decrease-key` via pointer handles is frequently slower than a "lazy deletion" binary heap (inserting duplicate `(dist, node)` tuples and discarding visited vertices) across realistic road network densities.
* Example candidate surprise: Memory allocation overhead dominating the theoretical gains of a structure unless arena/pool allocators are used, or observing unexpected amortized spikes in Pairing heap restructurings under specific edge ordering.



## 6. What We'd Do Next (~300–400 words)

* Cache-oblivious priority queues (e.g., Funnel heaps).
* Multi-threaded / concurrent Dijkstra variants (e.g., delta-stepping) and lock-free priority queue comparisons.
* Exploring SIMD vectorization for $d$-ary heap child scans.

## 7. Individual Contributions & AI Use Disclosures (~500 words)

* **Attributions:** Per-member responsibilities across implementation, harness architecture, profiling, and report sections.
* **AI disclosure:**
* Per-member tool usage statement.
* Three concrete examples where AI generated broken/misleading code or logic.
* Reflection on AI's impact on group coordination and verification.

Standalone Individual Deliverables

    Individual Reflection Document (~500 words)

        Submitted as a separate document alongside the group artifacts.

        Focuses exclusively on your own assigned algorithm.

        Must answer these four prompts concretely:

            What's the worst case for your algorithm, and what kind of input triggers it?

            What was the hardest bug or design decision you encountered, and how did you resolve it?

            If you did this implementation again from scratch, what would you do differently?

            What's one thing about your algorithm that you didn't fully understand before starting, and now do?

        Grading weight: 5% (marked strictly on technical depth and specificity).

    Peer Viewing Responses (~600 words total, due Week 5)

        Completed individually after videos are submitted.

        Watch 3 other groups' videos assigned to you and write ~200 words per video addressing:

            What problem did this group work on, and what algorithms did they compare?

            What did they find that you thought was interesting or surprising?

            What is one thing you would have done differently, or one question their work raised that they didn't answer?

        Grading weight: 5%.
