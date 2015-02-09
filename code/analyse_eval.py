#!/usr/bin/env python

#
# Analyse results of human evaluation
#

import csv

def main():
  data_dir = "../data/"
  seed_str = "seed"
  for annotator in "0","1":
    eval_stem = data_dir + "eval." + seed_str + "." + annotator
    key_file = eval_stem + ".key.csv"
    eval_file =  eval_stem + ".csv.out"
    ref_file =  eval_stem + ".ref"
    base_better,ape_better,same = [],[],[]
    for key_line,eval_line,ref_line in zip(\
        csv.reader(open(key_file)), csv.reader(open(eval_file)),\
        open(ref_file)):
      first,second,count = key_line
      count = int(count)
      source,base_text,ape_text,result = eval_line      
      if first == "1":
        #swap
        base_text,ape_text = ape_text,base_text
        if result == "0": result = "1"
        elif result == "1": result ="0"
      example = [(source,base_text,ape_text,ref_line[:-1]),]
      if result == "0":
        base_better += example*count
      elif result == "1":
        ape_better += example*count
      else:
        same += example*count
    for label,seq in \
      ("Base better", base_better),\
      ("APE better", ape_better),\
      ("Same", same):
      print "****",label,"****"
      for ex in seq:
        print "\n".join(ex)
        print
    total = float(len(base_better) + len(ape_better) + len(same))/100
    print "SUMMARY: Annotator: %s  Base better: %d (%4.1f%%) APE better: %d (%4.1f%%) Same: %d (%4.1f%%)" % \
      (annotator,len(base_better), len(base_better)/total,
         len(ape_better),len(ape_better)/total, len(same),len(same)/total)


if __name__ == "__main__":
  main()

