#!/usr/bin/env python

#
# Batch decode with Moses, updating after each sentence. This script is set up to mimic
# the way Moses performs when run by mert-moses.pl
#

import argparse
import atexit
import logging
import os
import signal
import subprocess
import sys
import time
import xmlrpclib

import moses
import pyter

LOG = logging.getLogger(__name__)

def main():
  logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
#  parser = argparse.ArgumentParser(description = "Decode using post-editor")
#  parser.add_argument("-f", "--moses-config", help="Moses configuration", required=True)
#  parser.add_argument("-n", "--nbest-size", type=int)
#  parser.add_argument("-o", "--nbest-output", default="nbest")
#  parser.add_argument("-p", "--server-port", default="8080")
#  parser.add_argument("-i", "--input-file", required=True)
#  parser.add_argument("-r", "--reference-file", required=True)

#  args = parser.parse_args()
  args = {}
  curr = []
  for arg in sys.argv:
    if arg.startswith("-"):
      curr = []
      args[arg[1:]] = curr
    else:
      curr.append(arg)

  if args.has_key("show-weights"):
    moses_args = [moses.bin_dir + "/moses", "-config", args["config"][0], "-show-weights"]
    subprocess.check_call(moses_args)
    sys.exit(0)

  config = args['config'][0]
  port = "8080"
  reference_file = args['reference-file'][0]
  weights = args.get('weight-overwrite', [""])[0]
  nbest = args.get('n-best-list', ("","0"))
  nbest_file = nbest[0]
  nbest_size = int(nbest[1])
  source_file = args['input-file'][0]


  server_args = [moses.server, "-f", config, "-v", "1", "--server-port", port]
  if weights: server_args += ["-weight-overwrite",  weights]
  server = subprocess.Popen(server_args)#,stderr=open("/dev/null"))
  atexit.register(lambda : os.kill(server.pid, signal.SIGTERM))
  LOG.info("Waiting for server to start ...")
  time.sleep(20)
  LOG.info("..done")
  url = "http://localhost:%s/RPC2" % port
  proxy = xmlrpclib.ServerProxy(url)

  nbest_fh = None
  if nbest_size: nbest_fh = open(nbest_file, "w")
  line_no = 0
  for source,ref in zip(open(source_file),open(reference_file)):
    # Translate using Moses server
    params = {"text" : source}
    if nbest_fh: 
      params["nbest"] = nbest_size
      params["add-score-breakdown"] = 1
      params["nbest-distinct"] = 1
    result = proxy.translate(params)
    print result['text'].encode("utf8")
    if nbest_fh:
      for nbest_item in result['nbest']:
        print>>nbest_fh, line_no,"|||", nbest_item['hyp'].encode('utf8'), "|||", nbest_item['fvals'], "|||", nbest_item['totalScore']

    # Update foreground table
    source_tok = source.split()
    ref_tok = ref.split()
    align = pyter.teralign(source_tok,ref_tok)
    align = " ".join(["%d-%d" % (a[0],a[1]) for a in align])
    params = {"source" : source, "target" : ref, "alignment" : align}
    result = proxy.updater(params)

    line_no += 1
  if nbest_fh: nbest_fh.close()

if __name__ == "__main__":
  main()
