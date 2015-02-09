#!/usr/bin/env python

#
# Automatic post-editing interface
#

import atexit
from collections import Counter
from  math import log,exp
import os
import signal
import subprocess
import time
import xmlrpclib

import moses
import pyter
from extract_phrases import Extractor

class PostEditor(object):
  
  def edit(self, source, mt):
    """Provide an edited version of the mt output."""
    # A do-nothing post-editor
    return mt

  def add_example(self, source, mt, ref):
    """Provide an example that the APE can learn from"""
    pass

  def name(self):
    return "null"

  def reset(self):
    """Called at start"""
    pass

  def finalise(self):
    """Called at end"""
    pass

class CollectorPE(PostEditor):
  """Collect the examples into files"""
  def __init__(self,stem):
    self.ref_fh = open(stem + ".ref", "w")
    self.mt_fh = open(stem + ".mt", "w")
    self.align_fh = open(stem + ".aln", "w")

  def add_example(self,source,mt,ref):
    mt_tok = mt.split()
    ref_tok = ref.split()
    align = pyter.teralign(mt_tok,ref_tok)
    print>> self.ref_fh, ref
    print>>self.mt_fh,mt
    print>>self.align_fh," ".join(["%d-%d" % (a[0],a[1]) for a in align])


  def name(self):
    return "collect"

class ExtractorPE(PostEditor):
  """Run phrase extraction using TER alignment"""
  def __init__(self):
    pass

  def add_example(self,source,mt,ref):
    mt_tok = mt.split()
    ref_tok = ref.split()
    align = pyter.teralign(mt_tok,ref_tok)
    extractor = Extractor()
    for phr in extractor(mt_tok,ref_tok,align):
      if phr[-3] != phr[-2]:
        print " ".join(phr[-3]),"|||", " ".join(phr[-2])
    print

  def name(self):
    return "extractor"

class MatcherPE(PostEditor):
  """Count how many learnt phrases match later examples"""
  def __init__(self):
    self.source_phrases = Counter() # source tuples
    self.matches = Counter()
    self.max_len = 5

  def edit(self, source, mt):
    source_tok = source.split()
    for start in range(len(source_tok)):
      for end in range(start+1, max(len(source_tok)+1,start+self.max_len+1)):
        phrase = tuple(source_tok[start:end])
        if self.source_phrases[phrase]:
          self.matches[phrase] += 1
    return mt

  def add_example(self,source,mt,ref):
    mt_tok = mt.split()
    ref_tok = ref.split()
    align = pyter.teralign(mt_tok,ref_tok)
    extractor = Extractor(self.max_len)
    for phr in extractor(mt_tok,ref_tok,align):
      if phr[-3] != phr[-2]:
        self.source_phrases[tuple(phr[-3])] += 1

  def name(self):
    return "matcher"

  def finalise(self):
    for phrase,count in self.matches.most_common(20):
      print phrase,count
    print "Phrases matched: %d " % \
      (len(self.matches),)

class PhraseBasedPE(PostEditor):

  def __init__(self):
    self.model = "../model/moses-ident.ini"
    self.port = "8080"
    self.url = "http://localhost:%s/RPC2" % self.port
    self._start_server()

  def name(self):
    return "pb"

  def edit(self,source,mt):
    result = self.proxy.translate({"text":mt}) 
    return result['text']

  def add_example(self, source, mt, ref):
    mt_tok = mt.split()
    ref_tok = ref.split()
    align = pyter.teralign(mt_tok,ref_tok)
    
    params = {"source" : mt , "target" : ref, \
      "alignment" : " ".join(["%d-%d" % (a[0],a[1]) for a in align])}
    result = self.proxy.updater(params)
    #for phr in extractor(mt_tok,ref_tok,align):
      #if phr[-3] != phr[-2]:
        #print " ".join(phr[-3]),"|||", " ".join(phr[-2])

  def _start_server(self):
    args = [moses.server, "-f", self.model, "--server-port", self.port]#, "-v", "3"]
    self.server = subprocess.Popen(args,stderr=open("/dev/null"))
    atexit.register(lambda : os.kill(self.server.pid, signal.SIGTERM))
    time.sleep(20)
    self.proxy = xmlrpclib.ServerProxy(self.url)
    

  def reset(self):
    self.server.terminate()
    self._start_server()

class Scorer(object):

  def add_segment(self, hypothesis, reference):
    pass


  def get_score(self):
    return 0

bleu_order = 4

class BleuScorer(Scorer):
  
  def __init__(self):
    self.scores = [0] * (bleu_order*2+1)
    self.segment_count = 0

  def add_segment(self,hypothesis,reference):
    hypo_tokens = hypothesis.split()
    ref_tokens = reference.split()
    hypo_ngrams = self._get_ngrams(hypo_tokens)
    ref_ngrams = self._get_ngrams(ref_tokens)
    for i in range(bleu_order):
      matches = hypo_ngrams[i] & ref_ngrams[i]
      self.scores[i*2] += sum(matches.values())
      self.scores[i*2+1] += max(0,len(hypo_tokens) - i)
    self.scores[-1] += len(ref_tokens)
    self.segment_count += 1


  def _get_ngrams(self,segment):
    ngrams = []
    for length in range(1,bleu_order+1):
      ngrams.append(Counter())
      for start in range(0,len(segment)):
        end = start + length
        if end < len(segment)+1:
          ngrams[-1][tuple(segment[start:end])] += 1
    return ngrams

  def _floor_log(self,x):
    if x <= 0:
      return log(0.01)
    else:
      return log(float(x)) 

  def get_score(self):
    #print self.scores
    logbleu = 0.0
    for i in range(bleu_order):
      logbleu += self._floor_log(self.scores[i*2]) \
         - self._floor_log(self.scores[i*2+1])
    logbleu /= bleu_order
    bp = 1.0 - float(self.scores[-1]) / self.scores[1]
    if bp < 0:
      logbleu += bp
    return exp(logbleu)* 100




def main():
  b = BleuScorer()
  print b._get_ngrams("I would like to score would like score".split())
  b.add_segment("Score this sentence please now now .", "Score this sentence now please .")
  print b.scores 
  b.add_segment("Score this sentence now better", "Score this sentence now please .")
  print b.scores 
  print b.get_score()

if __name__ == "__main__":
  main()
