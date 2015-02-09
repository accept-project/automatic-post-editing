#!/bin/sh

moses_home=/home/bhaddow/moses.new/
pe_home=/home/bhaddow/code/accept/post-editing

wdir=$pe_home/tuning/tune.noseed.0

rm -r $wdir


input=$pe_home/data/edinpe_b.mt.en
ref=$pe_home/data/edinpe_b.ref0.en
ini=$pe_home/model/moses-ident.ini

$moses_home/scripts/training/mert-moses.pl -working-dir $wdir -no-filter-phrase-table -mertdir $moses_home/dist/bin  -return-best-dev -batch-mira -decoder-flags="-reference-file $ref"  $input $ref  $PWD/decoder.py ini
