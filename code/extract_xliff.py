#!/usr/bin/env python
import sys,os,MySQLdb,random
import xmlrpclib,HTMLParser,cgi
from matecat import *

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-dbase', help='name of mysql database',default="casmaccept_hytra_II")
    parser.add_argument('-user', help='mysql user name',default='readonly')
    parser.add_argument('-passwd', help='mysql password',default='ro-password')
    parser.add_argument('-flist', help="file list", default="files.list")
    # parser.add_argument('who',help='annotator name')

    args = parser.parse_args(sys.argv[1:])

    fnames = [x.strip() for x in open(args.flist)]

    DB = MateCat(args.dbase,args.user,args.passwd)
    T = {}
    for i,who in enumerate(['gabriella', 'steve']):
        P  = Project(DB,who)
        #print len(P.jobs)
        out = open('../data/annot_en%d.xliff'%i,'w')
        print >>out,'<?xml version="1.0" encoding="UTF-8"?>'
        print >>out, '<xliff version="1.2">'
        for i in xrange(len(P.jobs)):
            print >>out,P.jobs[i].xliff_str(fnames[i])
            pass
        print >>out,'</xliff>'
        pass
    pass
