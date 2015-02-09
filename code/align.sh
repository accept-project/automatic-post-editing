#!/bin/sh

for a in 0 1; do
  rm -f ../data/edinpe_a$a.*
  cp ../data/edinpe_a.mt.en ../data/edinpe_a$a.mt.txt
  cp ../data/edinpe_a.ref$a.en ../data/edinpe_a$a.ref.txt
  ./align.py ../data/edinpe_a.mt.en ../data/edinpe_a.ref$a.en > ../data/edinpe_a$a.mt-ref.symal
  for i in ../data/edinpe_a$a.*; do gzip $i; done
done
