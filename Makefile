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
VARIANTS = $(patsubst $(SRC_DIR)/%/,%,$(filter %/, $(wildcard $(SRC_DIR)/*/)))
BIN_VARIANTS = $(addprefix $(BIN_DIR)/,$(VARIANTS))
CSV_VARIANTS = $(VARIANTS:%=$(DATA_OUT_DIR)/%.csv)

# helper function
OBJS_FOR_SRCS = $(patsubst $(SRC_DIR)$(1)/%.c,$(BUILD_DIR)$(1)/%.o,$(wildcard $(SRC_DIR)$(1)/*.c))

COMMON_OBJS = $(call OBJS_FOR_SRCS,)

# generated test data vars:
SEED = 67

tiny_dense = -n 50     -m 20     -w 10
small_med  = -n 2000   -m 40000  -w 50
mod_sparse = -n 100000 -m 400000 -w 100
big_sparse = -n 100000 -m 400000 -w 1000
big_chungus = -n 1000000 -m 400000 -w 1000
little_chungus = -n 10 -m 10 -w 1000

TEST_SET  = tiny_dense small_med mod_sparse big_sparse big_chungus little_chungus
TEST_SRCS = $(patsubst %,$(TEST_SRC_DIR)/%.c,$(TEST_SET))
TEST_OBJS = $(patsubst %,$(TEST_BUILD_DIR)/%.o,$(TEST_SET))

.PHONY:
all: tests report

.PHONY:
tests: $(CSV_VARIANTS)

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
$(TEST_SRCS): $(TEST_SRC_DIR)/%.c:
	@printf "$(GREEN)generating $(WHITE)$*$(GREEN) tests $(RESET)\n"
	mkdir -p $(dir $@)
	./gen.py $* $($(*)) -s "$(SEED)" -o "$@"

$(TEST_OBJS): $(TEST_BUILD_DIR)/%.o: $(TEST_SRC_DIR)/%.c
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

$(CSV_VARIANTS): $(DATA_OUT_DIR)/%.csv: $(BIN_DIR)/% $(TEST_OBJS)
	@printf "$(GREEN)========================================\n"
	@printf "Running benchmark: $(WHITE)$*$(GREEN)\n"
	@printf "========================================$(RESET)\n"
	mkdir -p $(dir $@)
	-$< --output=$@

DEPS = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.d,$(wildcard $(SRC_DIR)/**/*.c))

-include $(DEPS)

-include $(patsubst %,$(TEST_BUILD_DIR)/%.d,$(TEST_SET))
