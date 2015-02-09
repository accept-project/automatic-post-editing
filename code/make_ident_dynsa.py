#!/usr/bin/env python

#
# Make the background suffix array table. It's the identity phrase table for the mt output
#

import os
import subprocess
import sys

import moses

def main():
  data_dir = "../data"
  model_dir = "../model"
  mt_file = data_dir + "/edinpe.mt.en"
  out_stem = "ident"
  ext = "mt"
  ext2 = "ref"


  # Create the identity alignment
  align_file = "%s/%s.aln" % (data_dir,out_stem)
  afh = open(align_file, "w")
  for line in open(mt_file):
    toks = len(line[:-1].split())
    print>>afh," ".join(["%d-%d" % (i,i) for i in xrange(toks)])
  afh.close()

  # Create suffix array
  args = [moses.bin_dir + "/mtt-build", "-i", "-o", "%s/%s.mm.%s" % (model_dir,out_stem,ext)]
  mtfh = open(mt_file)
  subprocess.check_call(args, stdin=mtfh)
  args = [moses.bin_dir + "/mtt-build", "-i", "-o", "%s/%s.mm.%s" % (model_dir,out_stem,ext2)]
  mtfh = open(mt_file)
  subprocess.check_call(args, stdin=mtfh)

  args = [moses.bin_dir + "/symal2mam", "%s/%s.mm.%s-%s.mam" % (model_dir,out_stem,ext,ext2)]
  afh = open(align_file)
  subprocess.check_call(args,stdin=afh)

  args = [moses.bin_dir + "/mmlex-build", "%s/%s.mm" % (model_dir,out_stem), ext, ext2,\
              "-o",  "%s/%s.mm.%s-%s.lex" % (model_dir,out_stem,ext,ext2), \
              "-c", "%s/%s.mm.%s-%s.coc" % (model_dir,out_stem,ext,ext2)]
  subprocess.check_call(args)




if __name__ == "__main__":
  main()
