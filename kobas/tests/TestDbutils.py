#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
# Copyright by Mao Xizeng (maoxz@mail.cbi.pku.edu.cn)
# Created: 2004-12-29 10:09:51
# $Id: TestDbutils.py 465 2008-03-04 18:15:07Z lymxz $

__version__ = '$LastChangedRevision: 465 $'.split()[-2]

"""unittest for dbutils
"""

import unittest
from kobas import dbutils

class TestKodb(unittest.TestCase):

    def setUp(self):
        self._keggdb = dbutils.keggdb()

    def testIsValidTrueAnnot(self):
        ''' test whether a tupple (gene_id, ko_id) is valid:
        true if in kg table, and false not in kg table.
        '''
        annot_case_true = ('hsa:124', 'K00001')
        self.assert_(self._keggdb.is_valid_annot(annot_case_true))

    def testIsValidFalseAnnot(self):
        """ test is_valid_annot for false annotation
        """
        annot_case_false = ('hsa:124', 'K00002')
        self.failIf(self._keggdb.is_valid_annot(annot_case_false))
        
        
    def testIsValidNullAnnot(self):
        """test is_valid_annot for null annotation
        """
        annot_case_null = ('hsa:124',)
        self.failIf(self._keggdb.is_valid_annot(annot_case_null), 'null test')

    def testKo3term2pathwayid(self):
        ko3term = 'Starch and sucrose metabolism'
        pathway_id = 'ko00500'
        self.failUnlessEqual(self._keggdb.ko3term2pathwayid(ko3term), pathway_id)

    def testGetKoName(self):
        koid1 = 'K00001'
        koname1 = 'E1.1.1.1, adh'
        koid2 = 'K00002'
        koname2 = 'E1.1.1.2, adh'
        self.failUnlessEqual(self._keggdb.get_ko_name(koid1), koname1)
        self.failUnlessEqual(self._keggdb.get_ko_name(koid2), koname2)
        

if __name__ == "__main__":
    unittest.main()
