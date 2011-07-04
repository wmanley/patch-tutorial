#!/bin/sh -e

nosetests *.py

for i in tests/*/run.sh
do
	( cd $(dirname $i) && ../../"$i" )
done

