CC=gcc
CFLAGS=-O3 -march=native -Wall -Wextra

all:
	$(CC) $(CFLAGS) sapphire/bfasm.c -o sapphire/bfasm
