#!/bin/sh

#
# Test that it can mimic Moses
#

./decoder.py -threads 4 -v 0 -config ../model/moses-ident.ini -show-weights
#./decoder.py -config ../model/moses-ident.ini -i ../data/edinpe.mt.en -r ../data/edinpe.ref0.en -n 100
