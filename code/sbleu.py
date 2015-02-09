#!/usr/bin/env python

#
# Plot sentence bleu for APE experiments
#

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import pandas
import subprocess

import moses
import tune_test

def get_sentence_bleu(ref_file, hyp_file):
  sbleu_bin = moses.bin_dir + "/sentence-bleu"
  sbleu_scores = []
  proc = subprocess.Popen([sbleu_bin, ref_file], stdin=open(hyp_file), stdout=subprocess.PIPE)
  for line in proc.stdout:
    sbleu_scores.append(float(line[:-1]))
  return sbleu_scores

def get_seed_str(seed):
  if seed: return "seed"
  else: return "noseed"

def get_col_ape(annotator,seed):
  col = "sbleu_" + get_seed_str(seed)
  col +=  annotator + "_ape"
  return col

def get_col_mt(annotator):
  col = "sbleu_"
  col +=  annotator + "_mt"
  return col

def main():
  scores = pandas.DataFrame() 
  mt_file = "../data/edinpe_c.mt.en"
  source_file = "../data/edinpe_c.fr"
  # Add mt & source
  scores["mt"] = [line[:-1] for line in open(mt_file)]
  scores["src"] = [line[:-1] for line in open(source_file)]
  for annotator in "0","1":
    ref_file = "../data/edinpe_c.ref%s.en" % annotator

    # Capture sentence bleu of mt
    sbleu_mt = get_sentence_bleu(ref_file, mt_file)
    scores[get_col_mt(annotator)] = sbleu_mt

    # Add ref
    scores["ref%s" % annotator] = [line[:-1] for line in open(ref_file)]

    # sentence bleu of ape
    for seed in True,False:
      tune_dir = tune_test.get_tune_dir("../",seed,annotator)
      ape_file = tune_dir + "/edinpe_c.out"
      sbleu_ape = get_sentence_bleu(ref_file, ape_file)
      scores[get_col_ape(annotator,seed)] = sbleu_ape

      # Add ape output
      scores["ape%s_%s" % (annotator,get_seed_str(seed))] = \
        [line[:-1] for line in open(ape_file)]

  pp = PdfPages("sbleu.pdf")
  for annotator in "0","1":
    for seed in True,False:
      title = "Annotator: %s; %s" % (annotator, get_seed_str(seed))
      print title
      fig = plt.figure(figsize=(8,6))
      diff_col = "diff_" + get_col_ape(annotator,seed)
      scores[diff_col] = scores[get_col_ape(annotator,seed)]-scores[get_col_mt(annotator)]
      #print scores.head(10)
      plt.plot(range(len(scores)),scores[diff_col])
      #plt.plot(pandas.rolling_mean(diff,50))
      for best,ascending in (("MT","APE"),(True,False)):
        print "Best for %s"  % best
        for rank,(ix,row) in enumerate(scores.sort(diff_col, ascending=ascending).head(20).iterrows()):
          print "Rank %d; Index %d" % (rank+1,ix)
          print "src mt ape ref"
          print row["src"]
          print row["mt"]
          print row["ape%s_%s" % (annotator,get_seed_str(seed))]
          print row["ref%s" % annotator]
          print "Bleu: MT: %7.5f APE: %7.5f Diff: %7.5f " % \
            (row[get_col_mt(annotator)], row[get_col_ape(annotator,seed)], row[diff_col])
          print
        
      plt.title(title)
      plt.ylabel("bleu(ape) - bleu(mt)")
      plt.xlabel("sentence id")
      pp.savefig(fig)
  pp.close()

if __name__ == "__main__":
  main()
