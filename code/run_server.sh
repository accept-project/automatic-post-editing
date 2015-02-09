#!/bin/sh


moses_version=070afad

model_dir=../model
moses_bin=/home/bhaddow/moses.new/dist/$moses_version/bin

nohup $moses_bin/mosesserver --server-port 8080 -f $model_dir/moses-empty.ini 2> ../logs/server.err > ../logs/server.log  &
