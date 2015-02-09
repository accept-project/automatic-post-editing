#!/usr/bin/env python

#
# Convert the xliff files to source, mt, target1 and target2
#

import tokenise
import xliff

stem = "../data/edinpe"

def deescape(sentence):
  #print sentence.encode("utf8")
  sentence = sentence.replace("& quot;","\"")
  sentence = sentence.replace("&quot;","\"")
  sentence = sentence.replace("&amp;","&")
  #print sentence.encode("utf8")
  #print
  return sentence

def main():

  tok = tokenise.Tokeniser()
  for annot in xliff.annots:
    annot["sources"] = []
    annot["targets"] = []
    annot["mts"] = []
    for sf in xliff.parse(annot["filename"]):
      for sentence in sf["sentences"]:
        if not sentence.has_key("mt"): continue
        source = tok.tokenise(deescape(sentence["source"]))
        mt = tok.tokenise(deescape(sentence["mt"]))
        target = tok.tokenise(deescape(sentence["target"]))
        annot["sources"].append(source)
        annot["targets"].append(target)
        annot["mts"].append(mt)

  # Merge the annotators
  # targets is a list of pairs
  mts, sources, targets = [],[],[]
  mt_diff_count = 0
  source_diff_count = 0
  empty_count = 0
  same_count = 0
  for i,mt in enumerate(zip(*[annot["mts"] for annot in xliff.annots])):
    if mt[0] != mt[1]: 
      mt_diff_count += 1
      continue
    source = [xliff.annots[0]["sources"][i], xliff.annots[1]["sources"][i]]
    if source[0] != source[1]: continue
    target = [xliff.annots[0]["targets"][i], xliff.annots[1]["targets"][i]]
    if len(target[0]) == 0 or len(target[1]) == 0:
      empty_count += 1
      continue
    if target[0] == "! SAME !" or target[1] == "! SAME !":
      same_count += 1
      continue
    sources.append(source[0])
    mts.append(mt[0])
    targets.append(target)
  print "Ignored %d segment(s) where MT differs, %d where at least one target is empty, and %d where segment marked 'SAME'" % (mt_diff_count,empty_count,same_count)


  sourcefh = open(stem + ".fr", "w")
  mtfh = open(stem + ".mt.en", "w")
  targetfh = [open(stem + ".ref0.en", "w"), open(stem + ".ref1.en", "w")]
  for  mt, source, target in zip(mts,sources,targets):
    print>>sourcefh,source
    print>>mtfh,mt
    print>>targetfh[0],target[0]
    print>>targetfh[1],target[1]
  for fh in sourcefh,mtfh,targetfh[0],targetfh[1]: fh.close()
    



if __name__ == "__main__":
  main()
