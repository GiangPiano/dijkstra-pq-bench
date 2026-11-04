#
# shell
#

SHELL := /usr/bin/env bash -O globstar

.PHONY:
all: report.pdf

report.pdf: $(shell ls **/*.tex)
	latexmk -pdf report.tex

.PHONY:
clean:
	-latexmk -C report.tex
