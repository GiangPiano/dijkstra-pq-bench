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

# all subdirs of source
VARIANTS = $(patsubst $(SRC_DIR)/%/,%,$(filter %/, $(wildcard $(SRC_DIR)/*/)))
BIN_VARIANTS = $(addprefix $(BIN_DIR)/,$(VARIANTS))
TEST_VARIANTS = $(addprefix test-,$(VARIANTS))

# helper function
OBJS_FOR_SRCS = $(patsubst $(SRC_DIR)$(1)/%.c,$(BUILD_DIR)$(1)/%.o,$(wildcard $(SRC_DIR)$(1)/*.c))

COMMON_OBJS = $(call OBJS_FOR_SRCS,)

# generated test data vars:
SEED = 67

tiny_dense = -n 50     -m 20     -w 10
small_med  = -n 2000   -m 40000  -w 50
mod_sparse = -n 100000 -m 400000 -w 100
big_sparse = -n 100000 -m 400000 -w 1000

DATA_SET  = tiny_dense small_med mod_sparse big_sparse
DATA_SRCS = $(patsubst %,$(DATA_DIR)/%.c,$(DATA_SET))
DATA_OBJS = $(patsubst %,$(DATA_DIR)/%.o,$(DATA_SET))

.PHONY:
all: test

.PHONY:
test: build data $(TEST_VARIANTS)

.PHONY:
data: $(DATA_FILES)

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
$(DATA_SRCS): $(DATA_DIR)/%.c:
	@printf "$(GREEN)generating $(WHITE)$*$(GREEN) tests $(RESET)\n"
	mkdir -p $(dir $@)
	./gen.py $* $($(*)) -s "$(SEED)" -o "$@"

$(DATA_OBJS): $(DATA_DIR)/%.o: $(DATA_DIR)/%.c
	mkdir -p $(dir $@)
	$(CC) -c $(CPPFLAGS) $(CFLAGS) $< -o $@

# object files
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	mkdir -p $(dir $@)
	$(CC) -c $(CPPFLAGS) $(CFLAGS) $< -o $@

# executable variants
.SECONDEXPANSION:
$(BIN_VARIANTS): $(BIN_DIR)/%: $(COMMON_OBJS) $(DATA_OBJS) $$(call OBJS_FOR_SRCS,/$$*)
	mkdir -p $(dir $@)
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

.PHONY: $(TEST_VARIANTS)
$(TEST_VARIANTS): test-%: $(BIN_DIR)/% data
	@printf "$(GREEN)========================================\n"
	@printf "Running benchmark: $(WHITE)$*$(GREEN)\n"
	@printf "========================================$(RESET)\n"
	-$<

DEPS = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.d,$(wildcard $(SRC_DIR)/**/*.c))

-include $(DEPS)

-include $(patsubst %,$(DATA_DIR)/%.d,$(DATA_SET))
