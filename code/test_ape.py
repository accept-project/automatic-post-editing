#!/usr/bin/env python

#
# Test an APE
#

import argparse
import logging
import os
import sys

import ape
from tokenise import Tokeniser
import xliff
from xliff_to_text import stem

LOG = logging.getLogger(__name__)

def get_ape(args):
  if args.type == "null":
    return ape.PostEditor()
  elif args.type == "pb":
    return ape.PhraseBasedPE()
  elif args.type == "collect":
    return ape.CollectorPE(args.collector_stem)
  elif args.type == "extract":
    return ape.ExtractorPE()
  elif args.type == "match":
    return ape.MatcherPE()

def main():
  parser = argparse.ArgumentParser(description = "Test automatic post-editing")

  parser.add_argument("-t", "--type", choices = ["null", "pb", "collect", "extract", "match"], default = "null")
  parser.add_argument("-c", "--collector-stem", default = "../data/ape",  help="Stem for output from collector")
  parser.add_argument("-v", "--verbose", action="store_true")
  parser.add_argument("-d", "--dump", help="Dump the post-edited output")
  args = parser.parse_args()

  logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
  if args.verbose:
    LOG.setLevel(logging.DEBUG)

  editor = get_ape(args)
  LOG.info("Post-editor: " + editor.name())

  dfh = None

  for annotator in "0","1":
    editor.reset()
    LOG.info("Annotator "+annotator)
    if args.dump:
      dfh = open(args.dump + ".ape" + annotator, "w")
    raw_score,edited_score = ape.BleuScorer(),ape.BleuScorer()

    count = 0
    for source,mt,ref in zip(open(stem + ".fr"), open(stem + ".mt.en"), open(stem + ".ref" + annotator + ".en")):
      source = source[:-1]
      mt = mt[:-1]
      ref = ref[:-1]
      LOG.debug("IN:  " + mt)
      edited_mt = editor.edit(source, mt)
      if type(edited_mt) == type(u""): edited_mt = edited_mt.encode("utf8")
      if dfh: print>>dfh,edited_mt
      LOG.debug("OUT: " + edited_mt)
      editor.add_example(source,mt,ref)
      raw_score.add_segment(mt, ref)
      edited_score.add_segment(edited_mt, ref)
      count += 1
      if count % 20 == 0:  sys.stderr.write(".")
      if count % 1000 == 0: sys.stderr.write(" [%d]\n" % count)

    print>>sys.stderr
    raw_bleu = raw_score.get_score()
    edited_bleu = edited_score.get_score()
    LOG.info("Segments: %d" %  raw_score.segment_count)
    LOG.info("Score of raw MT: %5.2f" % raw_bleu)
    LOG.info("Breakdown: "+ str(raw_score.scores))
    LOG.info("Score of post-edited MT: %5.2f"% edited_bleu)
    if dfh: dfh.close()
    editor.finalise()

if __name__ == "__main__":
  main()
