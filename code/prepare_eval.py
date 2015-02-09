#!/usr/bin/env python

#
# Prepare for human eval
#

import csv
import random
from collections import Counter

import tune_test


def main():
  random.seed()
  data_dir = "../data/"
  source_lines = [line[:-1].strip() for line in open(data_dir + "/edinpe_c.fr").readlines()]
  mt_lines = [line[:-1].strip() for line in open(data_dir + "/edinpe_c.mt.en").readlines()]
  for annotator in "0","1":
    # Only evaluate seeded
    seed_flag = True
    seed_str = "seed"
    eval_stem = data_dir + "eval." + seed_str + "." + annotator
    efh = csv.writer(open(eval_stem + ".csv", "w"))
    kfh = csv.writer(open(eval_stem + ".key.csv", "w"))
    rfh = open(eval_stem + ".ref", "w")
    tuples = Counter()
    ref_lines = [line[:-1].strip() for line in open(data_dir + "/edinpe_c.ref%s.en" % annotator).readlines()]
    refs = {}
    for i,line in enumerate(open(tune_test.get_tune_dir("../",seed_flag,annotator) + "/edinpe_c.out")):
      line = line[:-1].strip()
      if line != mt_lines[i]:
        eval_tuple = (source_lines[i],mt_lines[i],line)
        tuples[eval_tuple] += 1
        refs[eval_tuple] = ref_lines[i]
    for eval_tuple,count in tuples.iteritems():
      print>>rfh,refs[eval_tuple]
      key = ["0","1",count]
      if random.randint(0,1):
        eval_tuple = (eval_tuple[0],eval_tuple[2],eval_tuple[1])
        key = ["1","0",count]
      efh.writerow(eval_tuple)
      kfh.writerow(key)
        
if __name__ == "__main__":
  main()
