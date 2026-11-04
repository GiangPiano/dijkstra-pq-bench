// Priority Queues in Dijkstra's Algorithm: 15 minute presentation
//
// Build from the repository root (image paths are root-relative):
//   typst compile --root . presentation/slides.typ
//
// Speaker notes are included on every slide. To view them alongside the
// slides, add `config-common(show-notes-on-second-screen: right)` to the
// simple-theme call below.

#import "@preview/touying:0.8.0": *
#import themes.simple: *
#import "@preview/fletcher:0.5.8" as fletcher: diagram, edge, node

#let fig(path) = "../report/frozen_results/figures/report_charts/" + path

#show: simple-theme.with(
  aspect-ratio: "16-9",
  footer: [Priority queues in Dijkstra's algorithm],
  config-common(new-section-slide-fn: none),
)

#set text(font: ("Libertinus Serif"), size: 20pt)
#show raw: set text(size: 0.85em)

#let muted(body) = text(fill: gray.darken(30%), body)
#let author(name) = block(below: 0.9em, text(size: 0.7em, fill: gray.darken(10%), [Presented by #name]))
#let big(body) = text(size: 1.6em, weight: "bold", body)

#let clean-table(..args) = table(
  stroke: none,
  inset: (x: 0.6em, y: 0.45em),
  table.hline(stroke: 0.6pt),
  ..args,
  table.hline(stroke: 0.6pt),
)

// ---------------------------------------------------------------------------

#title-slide[
  #text(size: 1.5em, weight: "bold")[Priority Queues in Dijkstra's Algorithm]

  #v(0.3em)
  #muted[Does a better big-O give you a faster heap?]

  #v(1.2em)
  #text(size: 0.8em)[Oscar Chevalier #h(1em) Truong Giang Nguyen #h(1em) Tung Nguyen]

  #text(size: 0.6em, fill: gray)[41052 Advanced Algorithms, Programming Assignment 2]
]

// ===========================================================================
= Problem and algorithms

== The problem

- Shortest distance from one source to *every* vertex
- Directed graph, positive integer weights
- Dijkstra: repeatedly settle the *closest* unsettled vertex

#v(1em)
#align(center)[
  "Give me the closest vertex" #h(0.5em) → #h(0.5em) *a min-heap*
]
#v(0.5em)
#align(center, muted[Same Dijkstra, same graphs. Only the heap changes.])

#speaker-note[
  Single-source shortest paths. Dijkstra's loop is: pop the closest vertex,
  relax its edges. Everything outside the heap is identical across our runs,
  so any difference we measure comes from the heap.
]

== Two ways to update the queue

#grid(
  columns: (1fr, 1fr),
  gutter: 2em,
  [
    *Decrease-key*
    - One entry per vertex
    - Found a shorter path? Update it in place
    - Heap must know *where* each vertex is
  ],
  [
    *Lazy*
    - Just push the new distance again
    - Skip stale entries when popped
    - Queue can grow to $m$ entries
  ],
)

#v(1em)
#align(center, muted[We ran every heap both ways.])

#speaker-note[
  Decrease-key keeps the heap small but needs a lookup from vertex to entry.
  Lazy needs no lookup but carries duplicates. Fibonacci and pairing heaps are
  designed to make decrease-key cheap, so we expected them to like this mode.
]

== Four heaps

#align(center, clean-table(
  columns: 4,
  align: (left, left, center, left),
  [*Heap*], [*Author*], [*Decrease-key*], [*Memory layout*],
  table.hline(stroke: 0.3pt),
  [Binary], [Giang], [$O(log n)$], [One flat array],
  [Pairing], [Tung], [cheap$""^*$], [Pointer nodes],
  [Fibonacci], [Tung], [$O(1)^*$], [Pointer nodes],
  [Brodal-Okasaki], [Oscar], [$O(log n)$], [One cell buffer],
))
#align(center, text(size: 0.6em, fill: gray)[$""^*$ amortised])

#v(0.5em)
*Why compare?* Theory says Fibonacci is optimal for Dijkstra, $O(m + n log n)$.
#muted[Does that hold on real hardware?]

#speaker-note[
  Binary is the textbook array heap. Pairing and Fibonacci are the pointer
  heaps built for cheap decrease-key. Brodal-Okasaki is a functional heap with
  optimal worst-case bounds. Our question: does better asymptotic complexity
  turn into faster Dijkstra?
]

// ===========================================================================
= Deep dives

== Binary heap: the hidden second invariant
#author[Truong Giang Nguyen]

+ *Heap order:* every parent $<=$ its children
+ *Position map:* `pos[v]` is the array index of vertex `v`

#v(0.6em)
- Decrease-key only lowers a key, so it only ever *bubbles up*
- `pos` tells us where to start, in $O(1)$
- *Every* move in bubble and sink must also update `pos`

#v(0.6em)
#align(center)[*Miss one update* → decrease-key edits the wrong slot → wrong distances, silently]

#speaker-note[
  Invariant 1 is the one everyone knows. Invariant 2 is the one that makes
  decrease-key possible on an array. The bug if you break it is nasty: nothing
  crashes, you just get wrong shortest paths.
]

== Binary heap: move, don't swap
#author[Truong Giang Nguyen]

#grid(
  columns: (1fr, 1fr),
  gutter: 2em,
  [
    *Naive swap*
    - Swap child and parent each level
    - 2 writes + 2 `pos` writes per level
  ],
  [
    *Our version: a "slot"*
    - Hold the moving item aside
    - Shift parents down into the slot
    - Write the item *once* at the end
  ],
)

#v(1em)
- Children at $2i+1$, $2i+2$: no pointers, one contiguous allocation
- This `pos` bookkeeping is the "tax" lazy mode avoids

#speaker-note[
  Because the moving item is kept in a register, each level costs one data
  write and one pos write instead of a full swap. Lazy mode never calls
  decrease-key, so it never needs pos at all; that is the trade-off we test.
]

== Pairing heap: one pointer, two jobs
#author[Tung Nguyen]

Each node: `child`, `next`, `prev`

#v(0.4em)
- `prev` = left sibling, *or the parent* if I'm the first child
- Check `prev->child == me` to know which case
- So decrease-key can *cut a node out in $O(1)$*, then meld it with the root

#v(0.8em)
#align(center)[*Without `prev`*: to unlink a node, scan its whole sibling list]

#speaker-note[
  Meld is trivial: the larger root becomes the leftmost child of the smaller.
  The tricky part is cutting a node out of the middle of a child list in
  constant time, which is what the dual-purpose prev pointer buys us.
]

== Pairing heap: all the work happens in pop
#author[Tung Nguyen]

Push and decrease-key just meld at the root. Pop pays the bill:

#v(0.4em)
+ *Pass 1:* pair up siblings left to right #muted[(halves the number of trees)]
+ *Pass 2:* meld the pairs right to left into one tree

#v(0.8em)
#align(center)[*Why two passes?* Melding children one by one leaves a long child list, \
so the *next* pop is just as slow. Two-pass keeps pop at amortised $O(log n)$.]

#speaker-note[
  The heap is self-adjusting: there is no balance information stored anywhere.
  The two-pass pairing is what restores shape after a pop. A single naive pass
  can leave a long chain of children and destroys the amortised bound.
]

== Fibonacci heap: a lazy forest
#author[Tung Nguyen]

#let accent = aqua.darken(50%)
#let fnode(pos, key, name, marked: false) = node(
  pos,
  text(size: 0.8em, fill: if marked { white } else { black }, str(key)),
  name: name,
  shape: circle,
  radius: 0.85em,
  stroke: 0.8pt + if marked { gray.darken(50%) } else { black },
  fill: if marked { gray.darken(40%) } else { white },
)

#grid(
  columns: (1.25fr, 1fr),
  gutter: 1.5em,
  align: horizon,
  diagram(
    spacing: (1.35em, 1.9em),
    edge-stroke: 0.8pt,
    // min pointer
    node((2, -0.7), text(size: 0.75em, weight: "bold", fill: accent)[min], name: <min>),
    edge(<min>, <r3>, "-|>", stroke: accent + 1pt),
    // root list: circular, doubly linked
    fnode((0, 0), 7, <r7>),
    fnode((1, 0), 3, <r3>),
    fnode((4, 0), 17, <r17>),
    fnode((5, 0), 24, <r24>),
    edge(<r7>, <r3>, "<|-|>", stroke: accent + 1pt),
    edge(<r3>, <r17>, "<|-|>", stroke: accent + 1pt),
    edge(<r17>, <r24>, "<|-|>", stroke: accent + 1pt),
    edge(<r24>, <r7>, "<|-|>", stroke: (paint: accent, thickness: 1pt, dash: "dashed"), bend: -40deg),
    // children of 3
    fnode((1, 1), 18, <c18>, marked: true),
    fnode((2, 1), 52, <c52>),
    fnode((3, 1), 38, <c38>),
    edge(<r3>, <c18>, "-|>"),
    edge(<c18>, <c52>, "<->", stroke: 0.5pt + gray.darken(20%)),
    edge(<c52>, <c38>, "<->", stroke: 0.5pt + gray.darken(20%)),
    fnode((1, 2), 39, <c39>, marked: true),
    fnode((3, 2), 41, <c41>),
    edge(<c18>, <c39>, "-|>"),
    edge(<c38>, <c41>, "-|>"),
    // children of 17 and 24
    fnode((4, 1), 30, <c30>),
    edge(<r17>, <c30>, "-|>"),
    fnode((5, 1), 26, <c26>, marked: true),
    fnode((6, 1), 46, <c46>),
    edge(<r24>, <c26>, "-|>"),
    edge(<c26>, <c46>, "<->", stroke: 0.5pt + gray.darken(20%)),
    fnode((5, 2), 35, <c35>),
    edge(<c26>, <c35>, "-|>"),
  ),
  text(size: 0.8em)[
    *The layout*
    - Roots sit in a *circular, doubly linked* list
    - `min` points straight at the smallest root
    - Siblings are circular lists too; a parent keeps one `child` pointer
    - #box(baseline: 0.15em, circle(radius: 0.4em, fill: gray.darken(40%))) marked: has lost a child

    #v(0.3em)
    *Second trick: be lazy, tidy up in pop*
    - Push just splices a node into the root list: $O(1)$
    - Pop *consolidates*: link roots of equal degree until every degree is unique, like carrying in binary addition
  ],
)

#speaker-note[
  Unlike the other heaps this is a forest, not one tree. Every list is
  circular and doubly linked, so splicing anything in or out is a few pointer
  writes. The second idea is laziness: push and decrease-key never compare
  trees, they just drop nodes on the root list. Pop pays for it with
  consolidate, which uses the A[degree] array to link equal-degree trees,
  exactly like carries in binary addition. That leaves at most about log n
  roots. The cost is 56-byte nodes and lots of pointer chasing.
]

== Fibonacci heap: marks and cascading cuts
#author[Tung Nguyen]

*Invariant:* a node may lose *at most one* child before it is cut itself

#v(0.4em)
- Lose a child → become *marked*
- Lose a second → cut to the root list, and check the parent too (*cascade*)

#v(0.6em)
*Why it's needed:* degree $k$ ⇒ at least $F_(k+2)$ descendants ⇒ degree $<= 1.44 log_2 n$, \
so the fixed `A[64]` degree array used in pop is always big enough

#v(0.4em)
#align(center)[*Without it*: wide but hollow trees, degrees grow, pop slows down]

#speaker-note[
  Decrease-key itself is just a cut. The cascading cut is what stops repeated
  cuts from hollowing out a tree. That bound is the whole reason consolidation
  in pop is logarithmic, and why a 64-slot degree array is safe.
]

== Brodal-Okasaki: decrease-key without handles
#author[Oscar Chevalier]

A functional heap has *no handles*: you can't point at a node inside it.

#v(0.4em)
So decrease-key $(v: 9 → 4)$ becomes:
+ Push $(9, v)$ into a second, *negative* heap #muted[(a tombstone)]
+ Push $(4, v)$ into the normal heap

#v(0.4em)
*Invariant:* after every pop, if both minimums are equal, *cancel* them

#align(center)[*Without cancelling*, the stale $(9, v)$ would surface as the minimum]

#speaker-note[
  This is the key idea. The heap identifies entries purely by value, so
  Dijkstra passes the old distance in. Note the cost: one decrease-key means
  two inserts now, and two delete-mins later when they cancel. Remember this
  for the surprise section.
]

== Brodal-Okasaki: making it imperative
#author[Oscar Chevalier]

- Kept the skew-binomial structure: $O(1)$ push, $O(log n)$ pop
- Dropped bootstrapping: Dijkstra never melds two heaps
- Mutates in place instead of copying
- *All cells live in one buffer* with its own free list
- Links are *offsets*, not pointers, so the buffer can grow without breaking them

#v(0.6em)
#align(center, muted[Result: a handful of `malloc` calls per run, like the binary heap])

#speaker-note[
  The original is persistent. We kept the shape of the data structure but
  threw away purity wherever it cost performance. Relative indices are the
  trick that lets realloc move the whole buffer safely.
]

// ===========================================================================
= Results

== The binary heap won every single run

#grid(
  columns: (1.3fr, 1fr),
  gutter: 1.2em,
  align: horizon,
  image(fig("runtime/uniform_dense.png"), height: 300pt),
  [
    #text(size: 0.75em)[
      Decrease-key, mean runtime

      #clean-table(
        columns: 3,
        align: (left, right, right),
        [], [*sparse*], [*dense*],
        table.hline(stroke: 0.3pt),
        [Binary], [*0.70 ms*], [*1.64 ms*],
        [Pairing], [0.92 ms], [2.06 ms],
        [Fibonacci], [1.90 ms], [2.86 ms],
        [Brodal-Okasaki], [3.39 ms], [15.72 ms],
      )
    ]
    #v(0.3em)
    #text(size: 0.75em)[Same order on all 7 graphs, both modes.]
  ],
)

#speaker-note[
  This is uniform_dense: 10k vertices, 500k edges, the graph that should most
  favour cheap decrease-key. The ordering binary, pairing, Fibonacci,
  Brodal-Okasaki holds on every graph we generated, sparse, dense, grid, hub
  and layered.
]

== Lazy vs decrease-key

#align(center, image(fig("runtime/lazy_vs_decrease_key.png"), height: 275pt))

#text(size: 0.8em)[
  Above 1: decrease-key faster. Gap grows with density (binary: 1.27× sparse → 1.93× dense). \
  *Brodal-Okasaki is the only heap that prefers lazy.*
]

#speaker-note[
  For three heaps, decrease-key wins and the gap widens as stale entries pile
  up in lazy mode. Brodal-Okasaki goes the other way on every graph. We come
  back to why in a moment.
]

== Why? The slow heaps just do more work

#align(center, image(fig("mem/allocator_pressure.png"), height: 205pt))

#text(size: 0.85em)[
  - Pairing and Fibonacci: *one `malloc` per node* (10k to 66k). Binary and Brodal-Okasaki: under 10
  - IPC was about 1 for every heap, and binary even had the *highest* L1 miss rate. \
    The gap is how much work each heap does, not how well the CPU runs it
]

#speaker-note[
  Log scale. Note the cache result: miss rate alone did not explain the
  ranking. The slower heaps simply execute more instructions and allocations
  per Dijkstra run, so a lower miss percentage doesn't save them.
]

// ===========================================================================
= What surprised us

#focus-slide[
  The "better" heaps never caught up.
]

== No crossover, even at 50 edges per vertex

*We predicted:* on dense graphs, decrease-key calls dominate, so pairing overtakes binary.

#v(0.6em)
#align(center)[
  #grid(
    columns: 2,
    gutter: 3em,
    [#big[1.64 ms] \ #muted[binary]], [#big[2.06 ms] \ #muted[pairing]],
  )
]

#v(0.6em)
- No crossover on *any* graph
- Contiguous memory and small constants beat the better big-O

#speaker-note[
  This was our main hypothesis and it failed cleanly. Even on the densest
  graph, where decrease-key is called hundreds of thousands of times, the
  array heap is about 25% faster than the pairing heap.
]

== The twist: Brodal-Okasaki prefers *not* to decrease keys

#grid(
  columns: (1fr, 1fr),
  gutter: 2em,
  [
    *One relaxation, decrease-key*
    - Tombstone insert + new insert
    - Two delete-mins to cancel later
    - 15.72 ms on `uniform_dense`
  ],
  [
    *One relaxation, lazy*
    - One insert
    - One delete-min
    - *9.10 ms* on `uniform_dense`
  ],
)

#v(0.8em)
#align(center)[The cost of decrease-key depends on the *implementation*, \ not just the textbook bound.]

#speaker-note[
  Same theoretical bound, but simulating decrease-key with a negative heap
  roughly doubles the queue work, so skipping it is about 40% faster.
  Whether lazy or eager Dijkstra wins is a property of the heap, not just of
  the graph.
]

// ===========================================================================
= Next steps

== What we'd do next

#v(2em)
#align(center)[
  + Try a wider range of heap implementations, notably the imperative brodal,
    and variations of the existing implementations with different optimisations
    applied, to explore which optimisations had the greatest impact on which
    heaps.
  + Have `push` return a handle so decrease-key is correct and works similarly
    on all heaps.
  + Rerun on graphs far bigger than the cache to see if the binary heap's lead
    holds as cache performance degrades.
]

#speaker-note[
  One sentence only. The handle idea is from our future improvement section;
  the larger graphs test whether locality still decides the race once nothing
  fits in cache.
]
