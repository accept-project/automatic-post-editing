#!/usr/bin/env python

import os
import subprocess

class Tokeniser:
  def __init__(self,path = "/home/bhaddow/moses.new/scripts/tokenizer/tokenizer.perl", lang="en"):
    if not os.path.exists(path):
      raise RuntimeError("Does not exist: " + path)
    if not os.access(path, os.X_OK):
      raise RuntimeError("Not executable: " + path)
    self.process = subprocess.Popen(
      [path, "-l", lang, "-b"], stdin=subprocess.PIPE,
         stdout=subprocess.PIPE,stderr=open("/dev/null"))

  def tokenise(self, input):
    input += "\n";
    self.process.stdin.write(input.encode("utf8"))
    output = self.process.stdout.readline()
    return output[:-1]



