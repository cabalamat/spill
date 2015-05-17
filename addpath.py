# addpath.py

"""***
<addpath.py> is a small program for adding directories to the list to
be searched.

How to use addpath
==================

Assume you have python source files in directory ./someproject/src/
and projectwide library files in ./someproject/lib/ . You want files
in ./someproject/src/ to be able to include files in ./someproject/lib/
(but not the other way round, because library files shouldn't depend
on project files).

(1) At the bottom of this file add a line, e.g:

   addpath("../lib")

(2) put addpath.py into ./someproject/src/

(3) all *.py files in ./someproject/src/ which want to import files
in ./someproject/lib/ should import addpath.py before the library file,
e.g:

   #===== src/foo.py =====
   import baz # imports src/baz.py
   import addpath
   import bar # imports lib/bar.py

***"""

import sys, os.path
debug = False

def addpath(newPath):
    """ add a path to sys.path """
    if debug: print "addpath(newPath=%r)" % (newPath,)
    home = sys.path[0]
    p = os.path.join(home, newPath)
    p2 = os.path.normpath(p)
    if p2 not in sys.path: sys.path.append(p2)
    if debug: print "addpath(): p=%r p2=%r\n   sys.path=%r\n" % (p, p2, sys.path)

#---------------------------------------------------------------------
# add your paths here:

addpath("lib")


#end
