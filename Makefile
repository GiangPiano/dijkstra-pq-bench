# C compiler to use, we might want to switch to Clang
CC = gcc
# Compiler flags
CFLAGS = -Wall -Wextra -g
# Linker flags
LDFLAGS =

# clean and run don't produce an output file
.PHONY: clean run

# compile the main executable and run it
run: main
	./main

# the main executable requires each of these objects
# adding it as a dependency will cause it to be automatically compiled
main: djikstras.o

# remove main and all the object files
# if they don't exist, don't fail without using -f
clean:
	-rm main
	-rm *.o
