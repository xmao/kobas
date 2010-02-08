#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
# Copyright by Mao Xizeng (maoxz@mail.cbi.pku.edu.cn)
# Created: 2005-05-15 16:29:18
# $Id: TestFasta.py 465 2008-03-04 18:15:07Z lymxz $

__version__ = '$LastChangedRevision: 465 $'.split()[-2]

"""unit test for fasta.py
"""

from kobas.exception import FastaIOError
from kobas import fasta

from unittest import TestCase, main
from StringIO import StringIO

good_data = [">abc\naaaaaaaaaaaaaaaa\n",
             ]
bad_data = [">abc\naaaaaaa\n>bb\n>cc\ncccccccccccccc\n",
            ">abc\naaaaaaa\n>bb\n"
            ]

class TestCase(TestCase):

    def setUp(self):
        pass

    def testVerifyRight(self):
        for rec in good_data:
            fasta.verify(StringIO(rec))

    def testVerifyFalse(self):
        for rec in bad_data:
            self.failUnlessRaises(FastaIOError, fasta.verify, StringIO(rec))

if __name__ == "__main__":
    main()
