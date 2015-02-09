#!/usr/bin/env python

#
# Calculate distances between mt and target
#

import numpy as np
import matplotlib.mlab as mlab
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import sys

import pyter

import xliff


def main():
  pp = PdfPages("dist.pdf")
  for annot in xliff.annots:
    levs,ters = [],[]
    for sf in xliff.parse(annot["filename"]):
      for sentence in sf["sentences"]:
        if sentence.has_key("mt"):
          mt = sentence["mt"].split()
          target = sentence["target"].split()
          if mt and target:
            lev = pyter.edit_distance(mt,target)
            ter = pyter.ter(mt,target)
            levs.append(lev)
            ters.append(ter)
            if ter > 1:
              print>>sys.stderr,mt
              print>>sys.stderr,target
              print>>sys.stderr,ter
            print annot["name"],lev,ter
    fig = plt.figure(figsize=(8,6))
    n,bins,patches = plt.hist(levs,50,facecolor="blue")
    plt.title("Annotator %s" % annot["name"])
    plt.xlabel("Levenshtein distance")
    plt.ylabel("Segments")
    pp.savefig(fig)

    fig = plt.figure(figsize=(8,6))
    n,bins,patches = plt.hist(ters,50,range=(0,10),facecolor="blue")
    plt.title("Annotator %s" % annot["name"])
    plt.xlabel("Translation edit rate")
    plt.ylabel("Segments")
    pp.savefig(fig)

  pp.close()


if __name__ == "__main__":
  main()
