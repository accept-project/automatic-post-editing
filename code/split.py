#!/usr/bin/env python

#
# Split the pe data into 3
#

def main():
  stem = "../data/edinpe"
  length = 0
  for line in open(stem + ".fr"): length += 1
  split = length/3
  for suffix in "fr", "mt.en", "ref0.en", "ref1.en":
    count = 0
    parts = ["c", "b", "a"]
    ofh = None
    for line in open(stem + "." + suffix):
      if count % split == 0 and parts:
        ofh = open("%s_%s.%s" % (stem,parts.pop(),suffix), "w")
      print>>ofh,line[:-1] 
      count += 1

       



if __name__ == "__main__":
  main()
