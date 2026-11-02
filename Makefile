# C compiler to use, we might want to switch to Clang
CC = gcc
# Compiler flags
CFLAGS = -Wall -Wextra -g -MMD -MP -O3
# Linker flags
LDFLAGS = -lm

GREEN  = \033[32m
WHITE  = \033[37m
RESET  = \033[0m

# source directory
SRC_DIR = ./src
# build output directories
BUILD_DIR = ./build
BIN_DIR = ./bin
DATA_DIR = ./data
DATA_OUT_DIR = $(DATA_DIR)/out
TEST_SRC_DIR = $(DATA_DIR)/src
TEST_BUILD_DIR = $(DATA_DIR)/build

# all subdirs of source
VARIANTS = $(filter-out bench, $(patsubst $(SRC_DIR)/%/,%,$(filter %/, $(wildcard $(SRC_DIR)/*/))))
BIN_VARIANTS = $(addprefix $(BIN_DIR)/,$(VARIANTS))
PERF_BIN_VARIANTS = $(VARIANTS:%=$(BIN_DIR)/perf_%)
CSV_VARIANTS = $(VARIANTS:%=$(DATA_OUT_DIR)/%.csv)

# helper function
OBJS_FOR_SRCS = $(patsubst $(SRC_DIR)$(1)/%.c,$(BUILD_DIR)$(1)/%.o,$(wildcard $(SRC_DIR)$(1)/*.c))

COMMON_OBJS = $(call OBJS_FOR_SRCS,)

# generated test data vars:
SEED = 67

tiny_dense = -n 50     -m 1000   -w 10
small_med  = -n 2000   -m 40000  -w 50
mod_sparse = -n 100000 -m 400000 -w 100
big_sparse = -n 100000 -m 400000 -w 1000
perf_sparse = -n 50000 -m 200000  -w 100
perf_dense  = -n 50000 -m 6400000 -w 100

TEST_SET  = tiny_dense small_med mod_sparse big_sparse
TEST_SRCS = $(patsubst %,$(TEST_SRC_DIR)/%.c,$(TEST_SET))
TEST_OBJS = $(patsubst %,$(TEST_BUILD_DIR)/%.o,$(TEST_SET))

PERF_TEST_SET  = perf_sparse perf_dense
PERF_TEST_SRCS = $(patsubst %,$(TEST_SRC_DIR)/%.c,$(PERF_TEST_SET))
PERF_TEST_OBJS = $(patsubst %,$(TEST_BUILD_DIR)/%.o,$(PERF_TEST_SET))

ALL_TEST_SRCS = $(TEST_SRCS) $(PERF_TEST_SRCS)
ALL_TEST_OBJS = $(TEST_OBJS) $(PERF_TEST_OBJS)

.PHONY:
all: tests report

.PHONY:
tests: $(CSV_VARIANTS)

.PHONY:
plot:
	./src/bench/bench0/plot0.py -i $(DATA_OUT_DIR) -o report/figures/runtime

.PHONY:
perf-build: $(PERF_BIN_VARIANTS)

.PHONY:
perf-run: perf-build
	./src/bench/bench1/bench1.py -o data/out/perf/hardware_counters.csv

.PHONY:
perf-plot:
	./src/bench/bench1/plot1.py -i data/out/perf/hardware_counters.csv -o report/figures/perf

.PHONY:
perf: perf-run perf-plot

.PHONY:
build: $(BIN_VARIANTS)

.PHONY:
clean-bin:
	-rm -r $(BIN_DIR)

.PHONY:
clean-build:
	-rm -r $(BUILD_DIR)

.PHONY:
clean-data:
	-rm -r $(DATA_DIR)

.PHONY:
clean-output-data:
	-rm -r $(DATA_OUT_DIR)

.PHONY:
clean-report:
	$(MAKE) -C ./report clean

.PHONY: clean
clean: clean-bin clean-build clean-data clean-report

# For the latex report
.PHONY: report
report:
	$(MAKE) -C ./report

# generated data files
.SECONDEXPANSION:
$(ALL_TEST_SRCS): $(TEST_SRC_DIR)/%.c:
	@printf "$(GREEN)generating $(WHITE)$*$(GREEN) tests $(RESET)\n"
	mkdir -p $(dir $@)
	./src/bench/gen.py $* $($(*)) -s "$(SEED)" -o "$@"

$(ALL_TEST_OBJS): $(TEST_BUILD_DIR)/%.o: $(TEST_SRC_DIR)/%.c
	mkdir -p $(dir $@)
	$(CC) -c $(CPPFLAGS) $(CFLAGS) $< -o $@

# object files
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	mkdir -p $(dir $@)
	$(CC) -c $(CPPFLAGS) $(CFLAGS) $< -o $@

# executable variants
.SECONDEXPANSION:
$(BIN_VARIANTS): $(BIN_DIR)/%: $(COMMON_OBJS) $(TEST_OBJS) $$(call OBJS_FOR_SRCS,/$$*)
	mkdir -p $(dir $@)
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

.SECONDEXPANSION:
$(PERF_BIN_VARIANTS): $(BIN_DIR)/perf_%: $(BUILD_DIR)/dijkstra.o $(BUILD_DIR)/graph.o $(BUILD_DIR)/bench/bench1/bench1.o $(PERF_TEST_OBJS) $$(call OBJS_FOR_SRCS,/$$*)
	mkdir -p $(dir $@)
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

$(CSV_VARIANTS): $(DATA_OUT_DIR)/%.csv: $(BIN_DIR)/% $(TEST_OBJS)
	@printf "$(GREEN)========================================\n"
	@printf "Running benchmark: $(WHITE)$*$(GREEN)\n"
	@printf "========================================$(RESET)\n"
	mkdir -p $(dir $@)
	-$< --output=$@

DEPS = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.d,$(wildcard $(SRC_DIR)/**/*.c))

-include $(DEPS)

-include $(patsubst %,$(TEST_BUILD_DIR)/%.d,$(TEST_SET))
-include $(patsubst %,$(TEST_BUILD_DIR)/%.d,$(PERF_TEST_SET))
