#
# shell
#

SHELL := /usr/bin/env bash -O globstar

FIGURES_DIR         = ./figures
RUNTIME_FIGURES_DIR = $(FIGURES_DIR)/runtime
PERF_FIGURES_DIR    = $(FIGURES_DIR)/perf
MEM_FIGURES_DIR     = $(FIGURES_DIR)/mem

FIGURES = $(RUNTIME_FIGURES_DIR)/runtime.tex \
					$(PERF_FIGURES_DIR)/perf.tex \
					$(MEM_FIGURES_DIR)/mem.tex \

report.pdf: report.tex $(FIGURES)
	latexmk -pdf report.tex

# do nothing
$(FIGURES):

.PHONY:
clean:
	-latexmk -C report.tex
