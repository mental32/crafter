.PHONY: all build run clean

all: build

clean:
	-rm -v crater/*.c
	-rm -v crater/*.so

build:
	python setup.py build_ext --inplace

run: all
	python entry.py