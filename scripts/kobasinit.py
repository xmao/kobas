#!/usr/bin/env python
"""Usage: kobasinit [options]

Initialize KOBAS using the data in kobas-data package.

   -h  Show this help
   -d  The KOBAS data target directory, default to get it in kobasrc
       configuration file.
   -s  The kobas-data source directory, default is the current directory

Report bug to KOBAS Team <kobas@mail.cbi.pku.edu.cn>
"""

from os import system, listdir
from os.path import exists, isdir, isfile, join, dirname, basename
from sys import stdout, stderr, exit
from shutil import copy, copytree
from kobas.config import context

def get_dst_data_dir():
    return context['kobas_home']

def copydir(src, dst):
    if not exists(src):
        raise IOError, "%s not exists :-/" % src
    if exists(dst):
        raise IOError, "%s exists :-/" % dst
    copytree(src, dst, symlinks=True)

def copyfile(src, dst):
    if not exists(src):
        raise IOError, "%s not exists :-/" % src
    copy(src, dst)

def init_fasta(fasta, dst):
    if not exists(fasta):
        raise IOError, "%s not exists :-/" % fasta
    newdst = join(dst, basename(fasta))
    copyfile(fasta, newdst)
    try:
        system("formatdb -pT -i '%s' " % newdst)
    except:
        raise IOError, "%s execution error :-/" % "formatdb"

def init_sqlite(sql, db):
    if not exists(sql):
        raise IOError, "%s not exists :-/" % sql
    if exists(db):
        raise IOError, "%s exists :-/" % db
    try:
        system("sqlite3  %s < '%s'" % (db, sql))
    except:
        raise
        raise IOError, "%s execution error :-/" % "sqlite"

def init_static(src, dst):
    if not isdir(src):
        raise IOError, "Need directory, but file meeted"
    for name in listdir(src):
        if isdir(join(src,name)):
            copydir(join(src,name), join(dst, name))
        else:
            copyfile(join(src,name), join(dst, name))

def verify_kobas_data(src):
    dirs = ["db", "fasta", "static"]
    for d in dirs:
        if d not in listdir(src):
            print >>stderr, "Invalid KOBAS data source directory"
            print >>stderr, "Please refer to useage: kobasinit.py -h"
            exit(1)

if __name__ == "__main__":
    from sys import argv
    from getopt import getopt

    try:
        opts, args = getopt(argv[1:], "s:d:")
    except:
        print __doc__
        exit(1)
    else:
        dopts = dict(opts)

    if dopts.has_key('-h'):
        print __doc__
        exit(0)

    src = dopts.get('-s', './')
    dst = dopts.get('-d', get_dst_data_dir())

    if not exists(dst):
        system('install -d %s' % dst)

    verify_kobas_data(src)
    init_static(join(src,'static'), dst)
    init_sqlite(join(src, 'db', 'ko-dump.sql'), join(dst, 'kegg.dat'))
    init_fasta(join(src, 'fasta', 'keggseq.fasta'), dst)
