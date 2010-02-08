#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
# Copyright by Mao Xizeng (maoxz@mail.cbi.pku.edu.cn)
# Created: 2005-04-27 12:20:29
# $Id: pathway.py 465 2008-03-04 18:15:07Z lymxz $

__version__ = '$LastChangedRevision: 465 $'.split()[-2]

"""pathway parser for kegg pathway database
"""

from os import listdir
from os.path import exists, isdir, isfile, join
from re import split
from sets import Set as set

from utils import cut

class pathway(dict):
    
    components = {'pathways':'map',
                  'genes':'gene',
                  'orthologs':'orth',
                  'compounds':'cpd',
                  'reactions':'rn'}
    
    def __init__(self, name):
        dict.__init__(self)
        for key in pathway.components.keys():
            self[key] = []
        self.name = name
        
    def linked_pathways(self): return self['pathways']

    def genes(self): return self['genes']

    def orthologs(self): return self['orthologs']

    def compounds(self): return self['compounds']

    def reactions(self): return self['reactions']
    
def pathway_from_files(name, dirname):
    path = pathway(name)
    try:
        for key, suffix in pathway.components.items():
            f = open('%s.%s' % (join(dirname,name),suffix))
            path[key] = cut(f)
    except:
        raise IOError, 'path error'
    return path

def pathways_from_dir(dirname):
    pathways = {}
    for pathname in pathlist_from_dir(dirname):
        pathways[pathname] = pathway_from_files(pathname, dirname)
    return pathways

def is_pathway_file(filename):
    return filename and isfile(filename)

def pathlist_from_dir(dirname):
    try:
        # files = filter(isfile, listdir(dirname))
        files = listdir(dirname)
        pathlist = [split(r'[._]', f)[0] for f in files]
        return list(set(filter(None, pathlist)))
    except:
        raise IOError, 'path error'

if __name__ == "__main__":
    pass
