#!/usr/bin/env python

import pandas

def count_words(filename):
  """Word counts from a file"""
  lines = [line[:-1] for line in open(filename).readlines()]
  df = pandas.DataFrame(lines,columns=['text'])
  return df.text.apply(lambda x: pandas.value_counts(x.split())).sum(axis = 0)


def main():
  align_method = "ter"
  edits_file = "../data/" + align_method + ".edits"
  df = pandas.read_table(edits_file,sep=" ")
  df['src_tgt'] = df['src'].str.cat(df['tgt'],"/")
  print "*** Comparing MT with post-edited version ***"
  print "Total edits:"
  size = df.groupby(["type", "aid"]).size()
  for annot in 0,1:
    dels = size[('del', annot)]
    subs = size[('sub', annot)]
    ins = size[('ins', annot)]
    total = float(dels + subs + ins)/100
    print "Annot %d: Inserts: %d (%4.1f%%);  Deletes: %d (%4.1f%%); Subs: %d (%4.1f%%); Total: %d" % \
      (annot, ins, ins/total, dels, dels/total, subs, subs/total, dels+subs+ins)

  ff = lambda x: "%5.2f%%" % x
  print
  for_latex = pandas.DataFrame()
  head_size = 10
  #mt_words = count_words("../data/edinpe.mt.en")
  for annot in 0,1:
    print "Annot %d:"%annot
    #ref_words = count_words("../data/edinpe.ref%d.en" % annot)
    dels = df[(df.aid==annot) & (df.type=="del")].src
    ins = df[(df.aid==annot) & (df.type=="ins")].tgt
    subs_old = df[(df.aid==annot) & (df.type=="sub")].src
    subs_new = df[(df.aid==annot) & (df.type=="sub")].tgt
    #mt_counts = pandas.DataFrame({ \
    #  'dels' :  dels.value_counts(), \
    #  'subs' : subs_old.value_counts(), \
    #  'totals' : mt_words})
    #ref_counts = pandas.DataFrame({\
    #  'ins' : ins.value_counts(), \
    #  'subs' : subs_new.value_counts(),
    #  'totals' : mt_words})
    for words,label in \
      (ins,"insertions"),\
      (dels,"deletions"),\
      (subs_old,"substituted (old)"),\
      (subs_new,"substituted (new)"),\
      (df[(df.aid==annot) & (df.type=="sub")].src_tgt,"substitutions"):
      print "Most frequent",label
      percents = 100.0*words.value_counts() / words.size
      print percents.head(10).to_string(float_format=ff)
      for_latex[label + "_" + str(annot)] = list(percents.head(head_size).index)
      for_latex[label + "_counts_" + str(annot)] = list(words.value_counts().head(head_size))
      print


  latex_fmt = lambda x: "{%s}" % str(x)
  print "Top n inserts/deletes"
  print for_latex.to_string(columns=("insertions_0", "insertions_counts_0","insertions_1","insertions_counts_1", "deletions_0", "deletions_counts_0", "deletions_1", "deletions_counts_1"), index=False, formatters = [latex_fmt] * 8)
  print "Top n subs"
  print for_latex.to_string(columns=("substitutions_0", "substitutions_counts_0", "substitutions_1", "substitutions_counts_1"), index=False, formatters = [latex_fmt] * 4)
  print

  print "*** Counting disagreements ***"
  a0 = df[df.aid==0]
  a1 = df[df.aid==1]
  merged_l = pandas.merge(a0, a1 , on = ["sid", "type", "src", "tgt", "src_tgt"], how="left")
  merged_r = pandas.merge(a0, a1 , on = ["sid", "type", "src", "tgt", "src_tgt"], how="right")
  only_0 = merged_l[merged_l.aid_y.isnull()]
  only_1 = merged_r[merged_r.aid_x.isnull()]
  head_size = 10
  for_latex = pandas.DataFrame()
  for annot, only in ((0,only_0), (1,only_1)):
    for label,counts in (\
      ("ins", only[only.type=="ins"].tgt.value_counts()),\
      ("del", only[only.type=="del"].src.value_counts()), \
      ("sub", only[only.type=="sub"].src_tgt.value_counts()),\
    ):
      #print "Inserted by annotator %d, not by other" % annot
      for_latex[label + "_" + str(annot)] = list(counts.head(head_size).index)
      for_latex[label + "_counts_" + str(annot)] = list(counts.head(head_size)) 

  print "Insertions/deletions by 1 annotator, but not other"
  cols = ["ins_0","ins_counts_0","ins_1", "ins_counts_1", "del_0","del_counts_0","del_1","del_counts_1"]
  print for_latex.to_string(index=False, columns=cols, formatters = len(cols)*[latex_fmt])

  print "Subtitutions by 1 annotator but not the other"
  cols = ["sub_0", "sub_counts_0", "sub_1", "sub_counts_1"]
  print for_latex.to_string(index=False, columns=cols, formatters = len(cols)*[latex_fmt])

  print
  print "*** Comparing Annotators ***"
  print "Total differences:"
  diffs_file = "../data/" + align_method + ".diffs"
  df = pandas.read_table(diffs_file, sep=" ")
  df['src_tgt'] = df['src'].str.cat(df['tgt'],"_")
  size = df.groupby(["type"]).size()
  print size
  annot0_ins =  size['del']
  annot1_ins =  size['ins']
  subs =  size['sub']
  total = float(annot0_ins + annot1_ins + subs)/100
  print "Inserted by annot 0: %d (%4.1f%%); Inserted by annot 1: %d (%4.1f%%); Subs: %d (%4.1f%%); Total: %d" % \
    (annot0_ins, annot0_ins/total, annot1_ins, annot1_ins/total, subs, subs/total, annot0_ins+annot1_ins+subs)
  print
  for words,label in \
      (df[df.type=="del"].src,"inserted by annot 0"),\
      (df[df.type=="ins"].tgt,"inserted by annot 1"),\
      (df[df.type=="sub"].src,"substituted (annot 0)"),\
      (df[df.type=="sub"].tgt,"substituted (annot 1)"),\
      (df[df.type=="sub"].src_tgt,"substitutions"):
    print "Most frequent",label
    percents = 100.0*words.value_counts() / words.size
    print percents.head(10).to_string(float_format=ff)
    print      


if __name__ == "__main__":
  main()
