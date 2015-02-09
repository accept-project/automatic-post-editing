#!/usr/bin/env python

#
# Read documents from xliff files
#

import xml.etree.ElementTree as ET

def parse(fh):
  """Generator to iterate through documents in xliff"""
  tree = ET.parse(fh)
  root = tree.getroot()
  for file_el  in root:
    source_file = {}
    source_file["name"]  = file_el.attrib['original']
    source_file["sentences"] = []
    for body_el in file_el.iter('body'):
      for trans_el in body_el.iter('trans-unit'):
        trans = {}
        for trans_subel in trans_el:
          if trans_subel.tag != "mt" or trans_subel.text.strip() != "?":
            text = trans_subel.text.strip()
            text = text.replace("\\\"", "\"")
            text = text.replace("\\\'", "\'")
            trans[trans_subel.tag] = text

        source_file["sentences"].append(trans)
    yield source_file
    
annots = [\
  {"name" : annot, "filename" : "../data/annot_%s.xliff" % annot}\
  for annot in "en0", "en1"]

#
# Collect some statistics on the documents
#  

def main():
  file_names = [] # sets
  for annot in annots:
    print "Annotator:",annot["name"]
    file_names.append(set())
    file_count = 0
    trans_count = 0
    src_count,tgt_count,mt_count,ident_count = 0,0,0,0
    for sf in parse(annot["filename"]):
      file_names[-1].add(sf["name"])
      file_count += 1
      for sentence in sf["sentences"]:
        trans_count += 1
        if sentence.has_key("source"): src_count+=1
        if sentence.has_key("target"): tgt_count+=1
        if sentence.has_key("mt"): mt_count+=1
        if sentence.get("target","") == sentence.get("mt",""): ident_count += 1
    print "File count: %d; Sentence count: %d" % (file_count, trans_count)
    print "Source sentences: %d; MT sentences: %d; Target sentences: %d; Identical: %d" % \
       (src_count,mt_count,tgt_count, ident_count)
    print
  print "Common files:", len(file_names[0].intersection(file_names[1]))


if __name__ == "__main__":
  main()
