# C compiler to use, we might want to switch to Clang
CC = gcc
# Compiler flags
CFLAGS = -Wall -Wextra -g -MMD -MP
# Linker flags
LDFLAGS =

# source directory
SRC_DIR = ./src
# build output directory
BUILD_DIR = ./build
BIN_DIR = ./bin

# all subdirs of source
VARIANTS = $(patsubst $(SRC_DIR)/%/,%,$(wildcard $(SRC_DIR)/*/))
VARIANT_BINS = $(addprefix $(BIN_DIR)/,$(VARIANTS))

OBJS_FOR_SRCS = $(patsubst $(SRC_DIR)$(1)/%.c,$(BUILD_DIR)$(1)/%.o,$(wildcard $(SRC_DIR)$(1)/*.c))

COMMON_OBJS = $(call OBJS_FOR_SRCS,)

.PHONY:
all: $(VARIANT_BINS)

.PHONY:
clean:
	-rm -r $(BIN_DIR)
	-rm -r $(BUILD_DIR)

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	mkdir -p $(dir $@)
	$(CC) -c $(CPPFLAGS) $(CFLAGS) $< -o $@

# builds
.SECONDEXPANSION:
$(VARIANT_BINS): $(BIN_DIR)/%: $(COMMON_OBJS) $$(call OBJS_FOR_SRCS,/$$*)
	mkdir -p $(dir $@)
	$(CC) $(LDFLAGS) $^ $(LOADLIBES) $(LDLIBS) -o $@

DEPS = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.d,$(wildcard $(SRC_DIR)/**/*.c))

-include $(DEPS)
