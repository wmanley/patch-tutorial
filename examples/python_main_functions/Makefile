#!/usr/bin/make

all : tutorial.html

.PHONY: all patches clean check

# Do what we came here to do: create a tutorial
tutorial.html : *.patch
	../../generate-patch-tutorial.py -o tutorial.html *.patch

# Converts a set of patches into a git repo for easier manipulation
repo : *.patch
	mkdir repo && cd repo && git init && cat ../*.patch | git am

# Reverses the effect of `make repo` creating patches from a git repo
patches :
	rm *.patch && cd repo && git format-patch -100 -o ..

# Check that each step leads to a well formed program that runs.  See check.sh
# for more information and motivations
check :
	set -e; mkdir check; cd check; for i in ../*.patch; do patch -p1 < "$$i"; ../check.sh; done; cd ..; rm -Rf check

clean :
	-rm -Rf repo check
	-rm tutorial.html
