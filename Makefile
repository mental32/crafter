ARTIFACTS := $(wildcard **/*.c) $(wildcard **/*.so)

.PHONY: all build run clean

all: build

rebuild:
	make clean
	make run

clean:
	-rm -v $(ARTIFACTS)
	python setup.py clean --all

build:
	python setup.py build_ext --inplace

run: all
	python -m crafter