#
# shell
#

SHELL := /usr/bin/env bash -O globstar

.PHONY:
all: report.pdf

report.pdf: $(shell echo **/*.tex) references.bib $(shell echo frozen_results/**/*)
	latexmk -pdf report.tex

.PHONY:
clean:
	-latexmk -C report.tex
