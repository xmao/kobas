#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
# Copyright by Mao Xizeng (maoxz@mail.cbi.pku.edu.cn)
# Created: 2005-03-24 13:14:23
# $Id: kpath.py 465 2008-03-04 18:15:07Z lymxz $

__version__ = '$LastChangedRevision: 465 $'.split()[-2]

"""KEGG pathway mining based on KO
"""

from glob import glob
from os.path import join

from kobas.config import getrc
from kobas.kgml import kgml
from pygraphlib import pygraph, algo, pydot

kg = kgml(join(getrc()['dat_dir'], 'data', 'kgml'))

def dgraph_from_kgml():
    pathways = kg.get_pathways('ot')
    edges = []
    for k, v in pathways.items():
        for l in v.get_linked_pathways():
            edges.append((k, l.name))
    return pygraph.from_list(edges)
    
if __name__ == "__main__":
    pass
