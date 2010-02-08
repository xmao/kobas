#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
# Copyright by Mao Xizeng (maoxz@mail.cbi.pku.edu.cn)
# Created: 2005-05-15 16:07:53
# $Id: exception.py 465 2008-03-04 18:15:07Z lymxz $

__version__ = '$LastChangedRevision: 465 $'.split()[-2]

"""exception class for kobas
"""

from sys import stderr

class FastaIOError(IOError):
    """ IOError exception for fasta file
    """
    pass


class AnnotError(Exception):
    """ AnnotError exception to support data restore, including the last queried
    seqence and current annotations
    """

    def __init__(self, annot, data):
        self.query = annot.query
        self.data = data

    def __str__(self):
        return "Unexpected stream after %s sequence" % self.query

class StatError(ArithmeticError):
    pass

def error(msg):
    err_msg = err_msg = '%s: %s\n' % (msg.__class__, msg)
    stderr.write(err_msg)

if __name__ == "__main__":
    pass
