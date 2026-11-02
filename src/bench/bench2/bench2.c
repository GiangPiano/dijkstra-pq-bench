/**
 * Bench2: Memory Footprint & Allocator Pressure Profiler for Dijkstra Heaps
 * Uses linker wrapping (-Wl,--wrap) to accurately capture heap allocations,
 * peak live heap bytes, allocator churn, and OS resident set size (Peak RSS).
 */

#define _GNU_SOURCE
#include <fcntl.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>

#include "../../dijkstra.h"
#include "../../graph.h"
#include "../bench0/bench0.h"

UBENCH_STATE();

extern const Graph* g_perf_sparse;
extern const Graph* g_perf_dense;

// ============================================================================
// Allocator Interposition (__wrap_malloc, __wrap_free, etc.)
// ============================================================================

extern void* __real_malloc(size_t);
extern void  __real_free(void*);
extern void* __real_calloc(size_t, size_t);
extern void* __real_realloc(void*, size_t);

typedef struct {
  size_t size;
  uint64_t magic;
} AllocHeader;

#define ALLOC_MAGIC 0xFEEDFACECAFEBEEFULL

static bool   g_tracking              = false;
static size_t g_malloc_count          = 0;
static size_t g_free_count            = 0;
static size_t g_realloc_count         = 0;
static size_t g_total_allocated_bytes = 0;
static size_t g_current_live_bytes    = 0;
static size_t g_peak_live_bytes       = 0;

void* __wrap_malloc(size_t sz) {
  size_t total = sizeof(AllocHeader) + sz;
  AllocHeader* hdr = (AllocHeader*)__real_malloc(total);
  if (!hdr) return NULL;

  hdr->size  = sz;
  hdr->magic = ALLOC_MAGIC;

  if (g_tracking) {
    g_malloc_count++;
    g_total_allocated_bytes += sz;
    g_current_live_bytes += sz;
    if (g_current_live_bytes > g_peak_live_bytes) {
      g_peak_live_bytes = g_current_live_bytes;
    }
  }

  return (void*)(hdr + 1);
}

void __wrap_free(void* ptr) {
  if (!ptr) return;
  AllocHeader* hdr = ((AllocHeader*)ptr) - 1;

  if (hdr->magic == ALLOC_MAGIC) {
    if (g_tracking) {
      g_free_count++;
      if (g_current_live_bytes >= hdr->size) {
        g_current_live_bytes -= hdr->size;
      } else {
        g_current_live_bytes = 0;
      }
    }
    hdr->magic = 0;
    __real_free(hdr);
  } else {
    __real_free(ptr);
  }
}

void* __wrap_calloc(size_t nmemb, size_t sz) {
  size_t total = nmemb * sz;
  void* p = __wrap_malloc(total);
  if (p) memset(p, 0, total);
  return p;
}

void* __wrap_realloc(void* ptr, size_t new_sz) {
  if (!ptr) return __wrap_malloc(new_sz);
  if (new_sz == 0) {
    __wrap_free(ptr);
    return NULL;
  }

  AllocHeader* hdr = ((AllocHeader*)ptr) - 1;
  size_t old_sz = (hdr->magic == ALLOC_MAGIC) ? hdr->size : 0;

  void* new_p = __wrap_malloc(new_sz);
  if (new_p) {
    if (g_tracking) g_realloc_count++;
    size_t copy_sz = (old_sz < new_sz) ? old_sz : new_sz;
    if (copy_sz > 0) memcpy(new_p, ptr, copy_sz);
    __wrap_free(ptr);
  }
  return new_p;
}

// ============================================================================
// Helper: Read VmHWM from /proc/self/status
// ============================================================================

static long get_proc_vmhwm_kib(void) {
  FILE* f = fopen("/proc/self/status", "r");
  if (!f) return -1;

  char line[256];
  long val = -1;
  while (fgets(line, sizeof(line), f)) {
    if (strncmp(line, "VmHWM:", 6) == 0) {
      sscanf(line + 6, "%ld", &val);
      break;
    }
  }
  fclose(f);
  return val;
}

// ============================================================================
// Main Execution Routine
// ============================================================================

int main(int argc, char* argv[]) {
  if (argc < 3) {
    fprintf(stderr, "Usage: %s <sparse|dense> <decrease_key|lazy>\n", argv[0]);
    return 1;
  }

  const char* config_name = argv[1];
  const char* mode_name   = argv[2];

  void (*dijkstra_fn)(int*, const Graph*) = NULL;
  if (strcmp(mode_name, "decrease_key") == 0) {
    dijkstra_fn = dijkstra_decrease_key;
  } else if (strcmp(mode_name, "lazy") == 0) {
    dijkstra_fn = dijkstra_lazy;
  } else {
    fprintf(stderr, "[ERROR] Unknown mode: %s\n", mode_name);
    return 1;
  }

  const Graph* g = (strcmp(config_name, "sparse") == 0) ? g_perf_sparse : g_perf_dense;
  if (!g) {
    fprintf(stderr, "[ERROR] Graph '%s' is NULL\n", config_name);
    return 1;
  }

  // Pre-allocate distance array outside of tracking
  int* dist = (int*)__real_malloc(sizeof(int) * g->num_vertices);
  if (!dist) {
    fprintf(stderr, "[ERROR] Failed to allocate dist array\n");
    return 1;
  }

  // Reset tracking stats
  g_malloc_count          = 0;
  g_free_count            = 0;
  g_realloc_count         = 0;
  g_total_allocated_bytes = 0;
  g_current_live_bytes    = 0;
  g_peak_live_bytes       = 0;

  struct timespec t_start, t_end;
  clock_gettime(CLOCK_MONOTONIC, &t_start);

  // START PROFILING
  g_tracking = true;
  dijkstra_fn(dist, g);
  g_tracking = false;
  // END PROFILING

  clock_gettime(CLOCK_MONOTONIC, &t_end);
  uint64_t elapsed_ns = (uint64_t)(t_end.tv_sec - t_start.tv_sec) * 1000000000ULL +
                        (uint64_t)(t_end.tv_nsec - t_start.tv_nsec);

  // Read OS Peak RSS
  struct rusage ru;
  getrusage(RUSAGE_SELF, &ru);
  long peak_rss_kib = ru.ru_maxrss;
  long vmhwm_kib = get_proc_vmhwm_kib();
  if (vmhwm_kib > 0) peak_rss_kib = vmhwm_kib;

  // Output CSV row
  // format: config,mode,peak_heap_bytes,total_allocated_bytes,malloc_count,free_count,realloc_count,leaked_bytes,peak_rss_kib,elapsed_ns
  printf("%s,%s,%zu,%zu,%zu,%zu,%zu,%zu,%ld,%" PRIu64 "\n",
         config_name,
         mode_name,
         g_peak_live_bytes,
         g_total_allocated_bytes,
         g_malloc_count,
         g_free_count,
         g_realloc_count,
         g_current_live_bytes,
         peak_rss_kib,
         elapsed_ns);

  __real_free(dist);
  return 0;
}
