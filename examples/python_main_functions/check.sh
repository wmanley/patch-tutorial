#!/bin/sh -e

#
# An example of how patch-tutorial can enable running automated tests on each
# tutorial step to check that it still works.  This can be useful when your
# tutorial depends on APIs that might be changing.
#
# This checking script will be run after each patch has been applied.  See the
# "check" rule in the Makefile to see how this is done.
#

# Here we might typically want to to a compile and test cycle, but in this
# simple case we just check that the program will run without error.
if python main.py; then
    echo SUCCESS
    exit 0
else
    echo FAIL
    exit 1
fi

