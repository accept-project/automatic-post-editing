#!/bin/sh

moses_version=070afad

data_dir=../data
model_dir=../model
moses_bin=/home/bhaddow/moses.new/dist/$moses_version/bin
stem=empty

$moses_bin/mtt-build -i -o $model_dir/$stem.mm.mt < $data_dir/$stem.mt
$moses_bin/mtt-build -i -o $model_dir/$stem.mm.ref < $data_dir/$stem.ref
$moses_bin/symal2mam $model_dir/$stem.mm.mt-ref.mam < $data_dir/$stem.aln
$moses_bin/mmlex-build $model_dir/$stem.mm mt ref -o $model_dir/$stem.mm.mt-ref.lex -c $model_dir/$stem.mm.mt-ref.coc


