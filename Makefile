#
# shell
#

SHELL:=/usr/bin/env bash -O globstar

#
# c compilation vars
#

# C compiler to use, we might want to switch to Clang
CC = gcc
# Compiler flags
CFLAGS = -Wall -Wextra -g -MMD -MP -O3 -std=c11
# Linker flags
LDFLAGS = -lm
# Alternate linker flags for memory profiling
MEM_LDFLAGS = $(LDFLAGS) -Wl,--wrap=malloc -Wl,--wrap=free \
							-Wl,--wrap=calloc -Wl,--wrap=realloc

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
OBJS_FOR_HEAP = $(patsubst $(HEAP_SRC_DIR)/%.c,$(HEAP_BUILD_DIR)/%.o,$(shell ls $(HEAP_SRC_DIR)$(1)/**/*.c))
# common objects for all executables
COMMON_OBJS = $(patsubst $(BENCH_SRC_DIR)/%.c,$(BENCH_BUILD_DIR)/%.o,$(wildcard $(BENCH_SRC_DIR)/*.c))

#
# generated test data
#

SEED = 67

tiny_dense  = -n 50     -m 1000    -w 10
small_med   = -n 2000   -m 40000   -w 50
mod_sparse  = -n 100000 -m 400000  -w 100
big_sparse  = -n 100000 -m 400000  -w 1000
sparse      = -n 50000  -m 200000  -w 100
dense       = -n 50000  -m 6400000 -w 100

TEST_SET  = tiny_dense small_med mod_sparse big_sparse sparse dense
TEST_SRCS = $(patsubst %,$(TEST_BUILD_DIR)/%.c,$(TEST_SET))
TEST_OBJS = $(patsubst %,$(TEST_BUILD_DIR)/%.o,$(TEST_SET))

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
PERF_CSV     = $(PERF_DATA_DIR)/hardware_counters.csv
MEM_CSV      = $(MEM_DATA_DIR)/memory_footprint.csv

.PHONY:
all: report

.PHONY:
build: $(RUNTIME_BIN_VARIANTS) $(PERF_BIN_VARIANTS) $(MEM_BIN_VARIANTS)

.PHONY:
csv: $(RUNTIME_CSVS) $(PERF_CSV) $(MEM_CSV)

.PHONY:
data: csv

.PHONY:
report: data
	$(MAKE) -C ./report

.PHONY:
clean:
	-rm -r $(BUILD_DIR)
	-rm -r $(BIN_DIR)
	-rm -r $(DATA_DIR)
	$(MAKE) -C ./report clean

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

# executable variants, each has a different entry point
.SECONDEXPANSION:
$(RUNTIME_BIN_VARIANTS): $(RUNTIME_BIN_DIR)/%: \
	$(BENCH_BUILD_DIR)/runtime/main.o $(COMMON_OBJS) $(TEST_OBJS) \
	$$(call OBJS_FOR_HEAP,/$$*)
	@mkdir -p $(dir $@)
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

.SECONDEXPANSION:
$(PERF_BIN_VARIANTS): $(PERF_BIN_DIR)/%: \
	$(BENCH_BUILD_DIR)/perf/main.o $(COMMON_OBJS) $(TEST_OBJS) \
	$$(call OBJS_FOR_HEAP,/$$*)
	@mkdir -p $(dir $@)
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

# alternate linker flags
.SECONDEXPANSION:
$(MEM_BIN_VARIANTS): $(MEM_BIN_DIR)/%: \
	$(BENCH_BUILD_DIR)/mem/main.o $(COMMON_OBJS) $(TEST_OBJS) \
	$$(call OBJS_FOR_HEAP,/$$*)
	@mkdir -p $(dir $@)
	$(CC) $(MEM_LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

# output csv data
$(RUNTIME_CSVS): $(RUNTIME_DATA_DIR)/%.csv: $(RUNTIME_BIN_DIR)/%
	@printf "$(GREEN)========================================\n"
	@printf "Running runtime benchmark: $(WHITE)$*$(GREEN)\n"
	@printf "========================================$(RESET)\n"
	@mkdir -p $(dir $@)
	$< --output=$@

$(PERF_CSV): $(PERF_BIN_VARIANTS) $(BENCH_SRC_DIR)/perf/bench.py
	@mkdir -p $(dir $@)
	$(BENCH_SRC_DIR)/perf/bench.py -o $@

$(MEM_CSV): $(MEM_BIN_VARIANTS) $(BENCH_SRC_DIR)/mem/bench.py
	@mkdir -p $(dir $@)
	$(BENCH_SRC_DIR)/mem/bench.py -o $@

$(RUNTIME_FIGURES_DIR)/%: $(RUNTIME_CSVS) $(BENCH_SRC_DIR)/runtime/plot.py
	$(BENCH_SRC_DIR)/runtime/plot.py -i $(RUNTIME_DATA_DIR) -o $(RUNTIME_FIGURES_DIR)

$(PERF_FIGURES_DIR)/%: $(PERF_CSVS) $(BENCH_SRC_DIR)/perf/plot.py
	$(BENCH_SRC_DIR)/perf/plot.py -i $(PERF_DATA_DIR) -o $(PERF_FIGURES_DIR)

$(MEM_FIGURES_DIR)/%: $(MEM_CSVS) $(BENCH_SRC_DIR)/mem/plot.py
	$(BENCH_SRC_DIR)/mem/plot.py -i $(MEM_DATA_DIR) -o $(MEM_FIGURES_DIR)

# include the .d makefiles of all ./src/**/*.c files
-include $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.d,$(shell ls $(SRC_DIR)/**/*.c))
# include the .d makefiles of all ./build/test/**/*.c files
-include $(patsubst %,$(TEST_BUILD_DIR)/%.d,$(TEST_SET))
