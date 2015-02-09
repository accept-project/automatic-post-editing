#!/usr/bin/env python

#
#
#

import pyter

def main():
  a = "a b c d e f g h i".split()
  b = "k c d m n e f g h p i".split()
  print pyter.edit_distance(a,b)
  a = "l e v e n s h t e i n".split()
  b = "m e i l e n s t e i n".split()
  print pyter.edit_distance(a,b)



if __name__ == "__main__":
  main()
