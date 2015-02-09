#!/usr/bin/env python

#
# Make an alignment of source and target
#

import sys

import pyter

def main():
  source_file = sys.argv[1]
  target_file = sys.argv[2]
  for source,target in zip(open(source_file),open(target_file)):
    source_tok = source[:-1].split()
    target_tok = target[:-1].split()
    align = pyter.teralign(source_tok,target_tok)
    align = " ".join(["%d-%d" % (a[0],a[1]) for a in align])
    print align



if __name__ == "__main__":
  main()
