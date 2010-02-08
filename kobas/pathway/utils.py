#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
# Copyright by Mao Xizeng (maoxz@mail.cbi.pku.edu.cn)
# Created: 2005-04-27 12:01:10
# $Id: utils.py 465 2008-03-04 18:15:07Z lymxz $

__version__ = '$LastChangedRevision: 465 $'.split()[-2]

"""some utils functions for parse pathway files
"""

from string import split

def cut(handle, field=1, sep='\t'):
    """ utility function by simulating gnu cut command
    """
    res = []
    for line in handle:
        fields = split(line, sep)
        if len(fields) >= field:
            res.append(fields[field-1].strip())
        else:
            res.append(None)
    return res

def tfilter(seq): return filter(None, seq)



if __name__ == "__main__":
    pass
    
