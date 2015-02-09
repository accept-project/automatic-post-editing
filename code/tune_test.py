#!/usr/bin/env python


import argparse
import logging
import moses
import os
import os.path
import shutil
import subprocess
import sys

LOG = logging.getLogger(__name__)

def get_tune_dir(home_dir, seed, annotator):
  wdir = home_dir + "/tuning/tune."
  if not seed: wdir += "no"
  wdir += "seed." + annotator
  return wdir
  

def main():
  logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
  parser = argparse.ArgumentParser(description = "Tune and test ape model")
  parser.add_argument("-d", "--home-dir", default="/home/bhaddow/code/accept/post-editing")
  args = parser.parse_args()
  for seed in True,False:
    if seed: LOG.info("With seeding")
    else: LOG.info("Without seeding")
    for annotator in "0","1":
      if seed and annotator=="0": continue
      LOG.info("Annotator " + annotator)

      # working directory
      wdir = get_tune_dir(args.home_dir,seed,annotator)
      if os.path.exists(wdir):
        shutil.rmtree(wdir)
      os.makedirs(wdir)

      # Tuning

      input_file = args.home_dir + "/data/edinpe_b.mt.en"
      ref_file = args.home_dir + "/data/edinpe_b.ref%s.en" % annotator
      ini_file = args.home_dir + "/model/moses-ident"
      if seed: ini_file += "-primed%s.ini" % annotator
      else: ini_file += ".ini"
      decoder = args.home_dir + "/code/decoder.py"
      margs = [moses.home_dir + "/scripts/training/mert-moses.pl", \
       "-working-dir", wdir,  "-no-filter-phrase-table", "-mertdir", moses.bin_dir, \
       "-return-best-dev", "-batch-mira", "-decoder-flags=-reference-file %s" % ref_file,
           input_file, ref_file,  decoder, ini_file]
      LOG.info("Running: " + " ".join(margs))
      subprocess.check_call(margs)


      # Fix ini file
      raw_ini_file = wdir + "/moses.ini"
      ini_file = wdir + "/moses.ini.fixed"
      ifh = open(ini_file,"w")
      rifh = open(raw_ini_file)
      ignoreNext = False
      for line in rifh:
        if line.startswith("[reference-file]"):
          ignoreNext = True
        elif not ignoreNext:
          print>>ifh,line[:-1]
        else:
          ignoreNext = False
      ifh.close()



      # Decoding

      input_file = args.home_dir + "/data/edinpe_c.mt.en"
      ref_file = args.home_dir + "/data/edinpe_c.ref%s.en" % annotator
      out_file = wdir + "/edinpe_c.out"
      outfh = open(out_file, "w")
      errfh = open(wdir + "/edinpe_c.err", "w")
      margs = [decoder, "-reference-file", ref_file, "-config", ini_file, "-input-file", input_file]
      subprocess.check_call(margs, stdout=outfh, stderr=errfh)
      outfh.close()
      errfh.close()

     # Evaluating
      LOG.info("BASE")
      subprocess.check_call([moses.home_dir + "/scripts/generic/multi-bleu.perl", ref_file], \
        stdin=open(args.home_dir + "/data/edinpe_c.mt.en")) 
      LOG.info("APE")
      subprocess.check_call([moses.home_dir + "/scripts/generic/multi-bleu.perl", ref_file], stdin=open(out_file)) 




if __name__ == "__main__":
  main()


