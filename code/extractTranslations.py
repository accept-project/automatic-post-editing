#!/usr/bin/env python
import sys,os,MySQLdb,random
import xmlrpclib,HTMLParser,cgi
from matecat import *

h = HTMLParser.HTMLParser()
def clean(s):
    return h.unescape(s.decode('utf8')).encode('utf8')

def process_file(who,f,T):
    for s in f.segments:
        if len(s.sugg):
            x = T.setdefault("%s"%(s.text.strip()), [])
            if s.sugg[0]["suggestion"]:
              x.append((s.sugg[0]["suggestion"].strip(),"sugg"))
            if len(s.trans):
                t = s.trans[0]['translation']
                if t: 
                    t = t.strip()
                    if len(t) and t.find('!SAME!') < 0 and (t,who) not in x:  
                        x.append((t,who))
                        pass
                    pass
                pass
            pass
        

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-dbase', help='name of mysql database',default="casmaccept_hytra_II")
    parser.add_argument('-user', help='mysql user name',default='readonly')
    parser.add_argument('-passwd', help='mysql password',default='ro-password')
    parser.add_argument("-output-dir", help='output directory', default='../data')
    # parser.add_argument('who',help='annotator name')

    args = parser.parse_args(sys.argv[1:])

    DB = MateCat(args.dbase,args.user,args.passwd)
    T = {}
    for who in ['gabriella','steve']:
        P  = Project(DB,who)
        for j in P.jobs:
            for f in j.files: 
                process_file(who,f,T)
                pass
            pass
        pass
    pool = [(s,t) for s,t in T.items()]
    idx = [i for i in xrange(len(pool))]
    random.shuffle(idx)
    ref = [open(args.output_dir+"/casmaccept.ref%d"%i,'w') for i in xrange(2)]
    src = open(args.output_dir+"/casmaccept.src",'w')
    mt  = open(args.output_dir+"/casmaccept.mt",'w')
    
    for i in idx:
        T = pool[i][1]
        if len(T) == 0: continue
        print >>src,clean(pool[i][0])
        g = [x[0] for x in T if x[1] == 'gabriella']
        s = [x[0] for x in T if x[1] == 'steve']
        sugg = [x[0] for x in T if x[1] == 'sugg']
        if not len(s): 
            s = g
            print "Missing steve"
            pass
        if not len(g):
            print "Missing gabriella"
            print 1,clean(pool[i][0])
            g = s
            pass
        print >>ref[0],clean(g[0])
        print >>ref[1],clean(s[0])
        if len(sugg):
          sugg = clean(sugg[0])
        else:
          print "Missing MT"
          sugg = ""
        print>>mt,sugg
        for k in xrange(1,max(len(g),len(s))-1):
            print >>src,clean(pool[i][0])
            print>>mt,sugg
            if len(g) > k:
                print >>ref[0],clean(g[k])
            else:
                print >>ref[0],clean(g[0])
                pass
            if len(s) > k:
                print >>ref[1],clean(s[k])
            else:
                print >>ref[1],clean(s[0])
                pass
            pass
        pass
    src.close()
    for r in ref: r.close()
    
