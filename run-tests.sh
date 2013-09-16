#!/bin/sh -e

nosetests *.py

for i in tests/*/run.sh
do
	echo -n "Running $i... "
	( cd $(dirname $i) && ../../"$i" ) && echo OK || echo FAILURE
done

