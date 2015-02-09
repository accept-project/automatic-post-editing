#!/usr/bin/env python

#
# Compare mt with targets, and targets with each other
#

from collections import Counter

import pyter

class Alignment:
  def __init__(self, source_toks, target_toks, aligns):
    """Initialise with list of source,target index pairs"""
    self._aligns = aligns
    self._source_toks = source_toks
    self._target_toks = target_toks

  def get_insertions(self):
    """All unaligned target words"""
    insertions = set(xrange(0,len(self._target_toks)))
    for si,ti in self._aligns:
      insertions.remove(ti)
    return [(i,self._target_toks[i]) for i in sorted(insertions)]

  def get_deletions(self):
    """All unaligned source words"""
    deletions = set(xrange(0, len(self._source_toks)))
    for si,ti in self._aligns:
      deletions.remove(si)
    return [(i,self._source_toks[i]) for i in sorted(deletions)]

  def get_substitutions(self):
    """All alignment points, where source and target are different"""
    subs = [(si,ti) for si,ti in self._aligns if \
        self._source_toks[si] != self._target_toks[ti]]
    return [(sub, (self._source_toks[sub[0]],self._target_toks[sub[1]])) for sub in subs]

  def __repr__(self):
    rep = ""
    for si,ti in sorted(self._aligns):
      rep = rep + "%s -> %s, " % (self._source_toks[si], self._target_toks[ti])
    return rep


class Aligner:
  def get_alignment(self,source,target):
    source_toks = source.split()
    target_toks = target.split()
    aligns = self._get_alignment(source_toks, target_toks)
    return Alignment(source_toks,target_toks,aligns)

  def _get_alignment(self,source_toks,target_toks):
    raise NotImplementedError

class EditDistanceAligner (Aligner):
  def __init__(self):
    self.name = "edist"

  def _get_alignment(self,source_toks,target_toks):
    dist,aligns = pyter.edit_distance(source_toks,target_toks)
    return aligns

class TerAligner (Aligner):
  def __init__(self):
    self.name = "ter"

  def _get_alignment(self,source_toks,target_toks):
    return pyter.teralign(source_toks,target_toks)

def main():
  data_dir = "../data/"
  #aligner = EditDistanceAligner()
  aligner = TerAligner()
  stem = aligner.name
  #align = aligner.get_alignment("The big red house", "The large house there")

  #print align.get_insertions()
  #print align.get_deletions()
  #print align.get_substitutions()
  mtfh = open(data_dir + "edinpe.mt.en")
  ref0fh = open(data_dir + "edinpe.ref0.en")
  ref1fh = open(data_dir + "edinpe.ref1.en")


  # compare the annotators with the mt 
  fh = open(data_dir + stem + ".edits", "w")
  print>>fh, "sid","aid","type","src","tgt"
  for sid,(mt,ref0,ref1) in enumerate(zip(mtfh,ref0fh,ref1fh)):
    for rid,ref in enumerate((ref0,ref1)):
      align = aligner.get_alignment(mt,ref)
      for indexes,tokens in align.get_substitutions():
        print>>fh, sid,rid,"sub",tokens[0],tokens[1]
      for index,token in align.get_deletions():
        print>>fh, sid,rid,"del",token,"-"
      for index,token in align.get_insertions():
        print>>fh, sid,rid,"ins","-",token
  fh.close()

  # compare the annotators to each other
  ref0fh = open(data_dir + "edinpe.ref0.en")
  ref1fh = open(data_dir + "edinpe.ref1.en")
  fh = open(data_dir + stem + ".diffs", "w")
  print>>fh,"sid","type","src","tgt"
  for sid,(ref0,ref1) in enumerate(zip(ref0fh,ref1fh)):
    align = aligner.get_alignment(ref0,ref1)
    for indexes,tokens in align.get_substitutions():
      print>>fh, sid,"sub",tokens[0],tokens[1]
    for index,token in align.get_deletions():
      print>>fh, sid,"del",token,"-"
    for index,token in align.get_insertions():
      print>>fh, sid,"ins","-",token
  fh.close()

if __name__ == "__main__":
  main()
