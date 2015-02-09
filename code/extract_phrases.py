#!/usr/bin/env python

#
# Standard algorithm for phrase extraction.
# Note that this produces the output in a different order from the Moses tool, since
# it maps source->target, whilst Moses maps target->source
#

from collections import defaultdict


#
# Given source,target sentence and list of alignment points, extract all compatible
# phrases.
# 
# input: aligns, lenE, lenF
# outputs: phrases
# phrases = []
# for startE in 0 .. lenE-1:
#   for endE in startE .. max(lenE-1, startE+maxLength-1):
#     minF = min(f: aligns(e) == f and startE <= e <= endE)
#     maxF = max(f: aligns(e) == f and startE <= e <= endE)
#   # Check if any f in [minF,maxF] has an alignment outside of [startE,endE)
#   out_of_bounds = False
#   for fi in minF .. maxF-1:
#     if aligns(e) == fi and (e < startE or e > endE): out_of_bounds = True
#   if not out_of_bounds:
#     # optionally include unaligned at the start/end
#     startF = minF
#     while startF >= 0 and endF-startF<=maxLength and (startF==minF || startF unaligned):
#       startF -= 1
#     endF = maxF
#     while endF < lenF and endF-startF<=maxLength and (endF==maxF || endF unaligned):
#       endF += 1
#     phrases.append((startE,endE,startF,endF)) 
#

class Extractor:
  def __init__(self,max_len=5):
    self.max_len = 5

  def __call__(self,source, target, align):
    """Generator for phrase extraction
      source and target should be sequences, align should be a sequence of pairs of integers"""
    lenS = len(source)
    lenT = len(target)
    alignS = defaultdict(set) # source->target
    alignT = defaultdict(set) # target->source
    for si,ti in align:
      alignS[si].add(ti)
      alignT[ti].add(si)
    for startS in range(lenS):
      for endS in range(startS, min(lenS,startS+self.max_len)):
#        print "Checking [%d,%d]" % (startS,endS)
        # find smallest and largest target words aligned to [startS,endS]
        minT = 1e10
        maxT = -1
        for si in range(startS,endS+1):
          if alignS[si]:
            minT = min(minT, min(alignS[si]))
            maxT = max(maxT, max(alignS[si]))
        if maxT < 0: continue
        #print "min,max",minT,maxT
        # there is an alignment point. check if any target is aligned outside of 
        # [startS,endS]
        out_of_bounds = False
        for ti in range(minT, maxT+1):
          for si in alignT[ti]:
            if si < startS or si > endS:
              out_of_bounds = True
              break
          if out_of_bounds: break
        if out_of_bounds: continue # ignore this candidate
        # retreat start across unaligned
        startT = minT
        while startT>=0 and startT+self.max_len > maxT and \
            (startT == minT or not alignT[startT]):
          # advance end over unaligned
          endT = maxT
          while endT < lenT and endT < startT + self.max_len and \
              (endT == maxT or not alignT[endT]):
            # find alignment points in the phrase pair
            phr_aligns = []
            for si in range(startS,endS+1):
              for ti in alignS[si]:
                phr_aligns.append((si-startS,ti-startT))
            yield startT,endT,startS,endS,source[startS:endS+1],target[startT:endT+1],phr_aligns
            endT += 1
          startT -= 1

def main():
  e = Extractor()
  for source,target,align in zip(open("test.extract.en"), open("test.extract.de"), open("test.extract.align")):
    source = source[:-1].split()
    target = target[:-1].split()
    align = [[int(i) for i in a.split("-")] for a in align[:-1].split()]
    for phr in e(source,target,align):
      print " ".join(phr[-3]),"|||"," ".join(phr[-2]),"|||",\
        " ".join("%d-%d" % a for a in sorted(phr[-1], key=lambda x: x[1]))

if __name__ == "__main__":
  main()
