#
# shell
#

SHELL := /usr/bin/env bash -O globstar
UNAME := $(shell uname)

#
# c compilation vars
#

# C compiler to use, we might want to switch to Clang
CC = gcc
# Compiler flags
CFLAGS = -Wall -Wextra -g -MMD -MP -O3 -std=c11
# Linker flags
LDFLAGS =
# Libraries go after the objects: linkers that default to --as-needed
# (Ubuntu, Debian, ...) drop a library named before the code that uses it
LDLIBS = -lm
# Alternate linker flags for memory profiling
MEM_LDFLAGS = $(LDFLAGS) -Wl,--wrap=malloc \
							-Wl,--wrap=free -Wl,--wrap=calloc -Wl,--wrap=realloc

#
# benchmark CPU pinning
#

# Benchmarks run pinned to one CPU so every graph sees the same caches. On
# Linux, bench_cpu.py picks a performance core (Intel hybrid or big.LITTLE)
# that this process is allowed to use; override with `make BENCH_CPU=<n>`, or
# `make BENCH_CPU=` to run unpinned. Without taskset (e.g. macOS) the
# benchmarks run unpinned.
ifeq "$(origin BENCH_CPU)" "undefined"
ifeq "$(UNAME)" "Linux"
BENCH_CPU := $(shell ./src/bench/bench_cpu.py 2>/dev/null)
endif
endif
TASKSET := $(shell command -v taskset 2>/dev/null)
PIN      = $(if $(and $(TASKSET),$(BENCH_CPU)),$(TASKSET) -c $(BENCH_CPU))

#
# cli colour vars
#

GREEN = \033[32m
WHITE = \033[37m
RESET = \033[0m

#
# build layout vars
#

# source directories
SRC_DIR       = ./src
BENCH_SRC_DIR = $(SRC_DIR)/bench
HEAP_SRC_DIR  = $(SRC_DIR)/heap
# build output directories
BUILD_DIR       = ./build
HEAP_BUILD_DIR  = $(BUILD_DIR)/heap
BENCH_BUILD_DIR = $(BUILD_DIR)/bench
TEST_BUILD_DIR  = $(BUILD_DIR)/test
# binaries directories
BIN_DIR         = ./bin
RUNTIME_BIN_DIR = $(BIN_DIR)/runtime
PERF_BIN_DIR    = $(BIN_DIR)/perf
MEM_BIN_DIR     = $(BIN_DIR)/mem

# all subdirs of src/heap
VARIANTS = $(patsubst $(HEAP_SRC_DIR)/%/,%,$(filter %/,$(wildcard $(HEAP_SRC_DIR)/*/)))

# all the different output executables
RUNTIME_BIN_VARIANTS = $(addprefix $(RUNTIME_BIN_DIR)/,$(VARIANTS))
PERF_BIN_VARIANTS    = $(addprefix $(PERF_BIN_DIR)/,$(VARIANTS))
MEM_BIN_VARIANTS     = $(addprefix $(MEM_BIN_DIR)/,$(VARIANTS))

# helper function to get expected .o files
# for a heap variant
OBJS_FOR_HEAP = $(patsubst $(HEAP_SRC_DIR)/%.c,$(HEAP_BUILD_DIR)/%.o,$(shell echo $(HEAP_SRC_DIR)$(1)/**/*.c))
# common objects for all executables
COMMON_OBJS = $(patsubst $(BENCH_SRC_DIR)/%.c,$(BENCH_BUILD_DIR)/%.o,$(wildcard $(BENCH_SRC_DIR)/*.c))

#
# generated test data
#

SEED = 67

smoke_1k         = --family uniform -n 1000 -m 4000 -w 50
uniform_sparse   = --family uniform -n 10000 -m 40000 -w 100
uniform_medium   = --family uniform -n 20000 -m 200000 -w 100
uniform_dense    = --family uniform -n 10000 -m 500000 -w 100
grid_224         = --family grid --rows 224 --cols 224 -w 100
hub_skewed       = --family hub_skewed -n 20000 -m 120000 --hubs 32 -w 100
layered_frontier = --family layered --layers 100 --width 200 --fanout 8 -w 100

smoke_1k_meta         = 'smoke_1k|uniform|1,000 vertices with a small uniform random frontier.|n=1000|m=4000|w=50'
uniform_sparse_meta   = 'uniform_sparse|uniform|Uniform sparse digraph (average out-degree 4).|n=10000|m=40000|w=100'
uniform_medium_meta   = 'uniform_medium|uniform|Uniform medium-density digraph (average out-degree 10).|n=20000|m=200000|w=100'
uniform_dense_meta    = 'uniform_dense|uniform|Uniform dense digraph (average out-degree 50).|n=10000|m=500000|w=100'
grid_224_meta         = 'grid_224|grid|224 x 224 four-neighbour directed grid.|rows=224|cols=224|w=100'
hub_skewed_meta       = 'hub_skewed|hub_skewed|Uniform background edges plus a concentrated 32-hub skew.|n=20000|m=120000|hubs=32|w=100'
layered_frontier_meta = 'layered_frontier|layered|100 layers of 200 vertices with deterministic forward fan-out.|layers=100|width=200|fanout=8|w=100'

TEST_SET  = smoke_1k uniform_sparse uniform_medium uniform_dense grid_224 hub_skewed layered_frontier
TEST_SRCS = $(patsubst %,$(TEST_BUILD_DIR)/%.c,$(TEST_SET))
TEST_OBJS = $(patsubst %,$(TEST_BUILD_DIR)/%.o,$(TEST_SET))

GRAPH_REGISTRY_SRC = $(TEST_BUILD_DIR)/graph_registry.c
GRAPH_REGISTRY_OBJ = $(TEST_BUILD_DIR)/graph_registry.o
GRAPH_METADATA     = $(TEST_BUILD_DIR)/graphs.json

#
# report and data outputs
#

REPORT_DIR          = ./report
DATA_DIR            = $(REPORT_DIR)/data
RUNTIME_DATA_DIR    = $(DATA_DIR)/runtime
PERF_DATA_DIR       = $(DATA_DIR)/perf
MEM_DATA_DIR        = $(DATA_DIR)/mem
FIGURES_DIR         = $(REPORT_DIR)/figures
RUNTIME_FIGURES_DIR = $(FIGURES_DIR)/runtime
PERF_FIGURES_DIR    = $(FIGURES_DIR)/perf
MEM_FIGURES_DIR     = $(FIGURES_DIR)/mem

# all the runtime csvs
RUNTIME_CSVS = $(patsubst %,$(RUNTIME_DATA_DIR)/%.csv,$(VARIANTS))

# can only run perf and mem on linux
ifeq "$(UNAME)" "Linux"
PERF_CSV     = $(PERF_DATA_DIR)/hardware_counters.csv
MEM_CSV      = $(MEM_DATA_DIR)/memory_footprint.csv
endif

ifeq "$(UNAME)" "Linux"
FIGURES = $(RUNTIME_FIGURES_DIR)/runtime.tex $(PERF_FIGURES_DIR)/perf.tex $(MEM_FIGURES_DIR)/mem.tex
else
FIGURES = $(RUNTIME_FIGURES_DIR)/runtime.tex
endif

.PHONY:
all: figures

.PHONY:
build: $(RUNTIME_BIN_VARIANTS) $(PERF_BIN_VARIANTS) $(MEM_BIN_VARIANTS)

.PHONY:
csvs: $(RUNTIME_CSVS) $(PERF_CSV) $(MEM_CSV)

.PHONY:
figures: $(FIGURES)

.PHONY:
clean:
	-rm -r $(BUILD_DIR)
	-rm -r $(BIN_DIR)
	-rm -r $(DATA_DIR)

# ./src/heap .c files -> ./build/heap .o files
$(HEAP_BUILD_DIR)/%.o: $(HEAP_SRC_DIR)/%.c
	@mkdir -p $(dir $@)
	$(CC) -c $(CPPFLAGS) $(CFLAGS) $< -o $@

# ./src/bench .c files -> ./build/bench .o files
$(BENCH_BUILD_DIR)/%.o: $(BENCH_SRC_DIR)/%.c
	@mkdir -p $(dir $@)
	$(CC) -c $(CPPFLAGS) $(CFLAGS) $< -o $@

# generated test source files
.SECONDEXPANSION:
$(TEST_SRCS): $(TEST_BUILD_DIR)/%.c: $(BENCH_SRC_DIR)/gen.py
	@printf "$(GREEN)generating $(WHITE)$*$(GREEN) test sources $(RESET)\n"
	@mkdir -p $(dir $@)
	$(BENCH_SRC_DIR)/gen.py $* $($(*)) -s "$(SEED)" -o "$@"

# generated test object files
$(TEST_OBJS): $(TEST_BUILD_DIR)/%.o: $(TEST_BUILD_DIR)/%.c
	@mkdir -p $(dir $@)
	$(CC) -c $(CPPFLAGS) $(CFLAGS) $< -o $@

$(GRAPH_REGISTRY_SRC) $(GRAPH_METADATA): $(TEST_SRCS) $(BENCH_SRC_DIR)/gen.py
	@mkdir -p $(dir $@)
	$(BENCH_SRC_DIR)/gen.py --registry "$(GRAPH_REGISTRY_SRC)" --metadata "$(GRAPH_METADATA)" --graphs $(TEST_SET) \
		$(foreach graph,$(TEST_SET),--metadata-entry $($(graph)_meta))

$(GRAPH_REGISTRY_OBJ): $(GRAPH_REGISTRY_SRC)
	@mkdir -p $(dir $@)
	$(CC) -c $(CPPFLAGS) $(CFLAGS) $< -o $@

# executable variants, each has a different entry point
.SECONDEXPANSION:
$(RUNTIME_BIN_VARIANTS): $(RUNTIME_BIN_DIR)/%: \
	$(BENCH_BUILD_DIR)/runtime/main.o $(COMMON_OBJS) $(TEST_OBJS) $(GRAPH_REGISTRY_OBJ) \
	$$(call OBJS_FOR_HEAP,/$$*)
	@mkdir -p $(dir $@)
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

.SECONDEXPANSION:
$(PERF_BIN_VARIANTS): $(PERF_BIN_DIR)/%: \
	$(BENCH_BUILD_DIR)/perf/main.o $(COMMON_OBJS) $(TEST_OBJS) $(GRAPH_REGISTRY_OBJ) \
	$$(call OBJS_FOR_HEAP,/$$*)
	@mkdir -p $(dir $@)
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

# alternate linker flags
.SECONDEXPANSION:
$(MEM_BIN_VARIANTS): $(MEM_BIN_DIR)/%: \
	$(BENCH_BUILD_DIR)/mem/main.o $(COMMON_OBJS) $(TEST_OBJS) $(GRAPH_REGISTRY_OBJ) \
	$$(call OBJS_FOR_HEAP,/$$*)
	@mkdir -p $(dir $@)
	$(CC) $(MEM_LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

# output csv data
$(RUNTIME_CSVS): $(RUNTIME_DATA_DIR)/%.csv: $(RUNTIME_BIN_DIR)/%
	@printf "$(GREEN)========================================\n"
	@printf "Running runtime benchmark: $(WHITE)$*$(GREEN)\n"
	@printf "Pinned to CPU: $(WHITE)$(if $(PIN),$(BENCH_CPU),none)$(GREEN)\n"
	@printf "========================================$(RESET)\n"
	@mkdir -p $(dir $@)
	$(PIN) $< --output=$@

# we can only run mem perf on linux, this keeps it all building on mac
ifeq "$(UNAME)" "Linux"
$(PERF_CSV): $(PERF_BIN_VARIANTS) $(BENCH_SRC_DIR)/perf/bench.py
	@mkdir -p $(dir $@)
	$(BENCH_SRC_DIR)/perf/bench.py -b $(PERF_BIN_DIR) -o $@ $(if $(BENCH_CPU),-c $(BENCH_CPU))
else
endif

ifeq "$(UNAME)" "Linux"
$(MEM_CSV): $(MEM_BIN_VARIANTS) $(BENCH_SRC_DIR)/mem/bench.py
	@mkdir -p $(dir $@)
	$(BENCH_SRC_DIR)/mem/bench.py -b $(MEM_BIN_DIR) -o $@
else
endif

$(RUNTIME_FIGURES_DIR)/runtime.tex: $(RUNTIME_CSVS) $(BENCH_SRC_DIR)/runtime/plot.py
	$(BENCH_SRC_DIR)/runtime/plot.py -i $(RUNTIME_DATA_DIR) -o $(RUNTIME_FIGURES_DIR)

$(PERF_FIGURES_DIR)/perf.tex: $(PERF_CSV) $(BENCH_SRC_DIR)/perf/plot.py
	$(BENCH_SRC_DIR)/perf/plot.py -i $(PERF_CSV) -o $(PERF_FIGURES_DIR)

$(MEM_FIGURES_DIR)/mem.tex: $(MEM_CSV) $(BENCH_SRC_DIR)/mem/plot.py
	$(BENCH_SRC_DIR)/mem/plot.py -i $(MEM_CSV) -o $(MEM_FIGURES_DIR)

# include the .d makefiles of all ./src/**/*.c files
-include $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.d,$(shell echo $(SRC_DIR)/**/*.c))
# include the .d makefiles of all ./build/test/**/*.c files
-include $(patsubst %,$(TEST_BUILD_DIR)/%.d,$(TEST_SET))
-include $(TEST_BUILD_DIR)/graph_registry.d
