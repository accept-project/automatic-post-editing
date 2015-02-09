#!/bin/sh


moses_version=070afad

data_dir=../data
model_dir=../model
moses_home=/home/bhaddow/moses.new/
moses_bin=$moses_home/dist/$moses_version/bin
wdir=/home/bhaddow/experiments/accept/symantec-baseline/lm/

#$moses_bin/lmplz --prune 0 0 1 -o 5 -S 10G -T /tmp < /home/bhaddow/experiments/accept/symantec.2014/lm/forum.tok.6 > $model_dir/forum.tok.en.lm
#$moses_bin/build_binary $model_dir/forum.tok.en.lm $model_dir/forum.tok.en.blm

lms=
for tok in forum.tok.14 europarl.tok.10 project-syndicate.tok.10; do
  lm=$model_dir/`echo $tok | sed 's/.tok.*//g'`.lm
  /home/bhaddow/tools/srilm-bin-i686-m64/ngram-count -order 5 -interpolate -kndiscount -text $wdir/$tok -lm $lm
done 

$moses_home/scripts/ems/support/interpolate-lm.perl --tuning $wdir/interpolate-tuning.tok.10 \
  --name $model_dir/interpolated.lm --srilm /home/bhaddow/tools/srilm-bin-i686-m64 \
  --lm $model_dir/forum.lm,$model_dir/europarl.lm,$model_dir/project-syndicate.lm

$moses_bin/build_binary $model_dir/interpolated.lm $model_dir/interpolated.blm
