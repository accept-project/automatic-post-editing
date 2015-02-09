#!/usr/bin/env python


#
# Calculate ter
#

import argparse
import sys

import pyter

def main():
  parser = argparse.ArgumentParser(description = "Compute TER score")
  parser.add_argument("-r", "--reference-file", help="Reference file", required=True)
  parser.add_argument("-m", "--hypothesis-file", help="Hypothesis file", required=True)
  args = parser.parse_args()

  line_count = 0
  total_ter = 0.0
  for hyp,ref in zip(open(args.hypothesis_file),open(args.reference_file)):
    ter,blah = pyter.ter(hyp[:-1].split(), ref[:-1].split())
    total_ter += ter
    line_count += 1

  print "Line count: %d Mean TER: %7.4f" % \
    (line_count, total_ter/line_count)
     


if __name__ == "__main__":
  main()



