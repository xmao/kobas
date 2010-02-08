#!/usr/bin/env python
"""unittest for annot"""

import unittest
from kobas import annot

class TestParseAnnot(unittest.TestCase):
    """ test for function parse_annot
    """

    def testParseNullAnnot(self):
        """test of parse_annot for null ko annot
        """
        annot_line = "ssr2130_synechocystis	"
        annot_obj = annot.parse_annot(annot_line)
        self.assertEqual(str(annot_obj), annot_line)

    def testParseSingleAnnot(self):
        """ test of parse_annot for single ko annot
        """
        annot_line = "sll0995_synechocystis	 K02316:51:6.3:31.6:0.314285714286"
        annot_obj = annot.parse_annot(annot_line)
        self.assertEqual(str(annot_obj), annot_line)

    def testParseMutipleAnnot(self):
        """ test of parse_annot for multiple ko annot
        """
        annot_line = "slr0399_synechocystis	 K00329:41:3e-06:53.5:0.26872246696 K00356:41:3e-06:53.5:0.26872246696"
        annot_obj = annot.parse_annot(annot_line)
        self.assertEqual(str(annot_obj), annot_line)

class TestAnnotation(unittest.TestCase):
    """ test for class Annotation
    """

    def testHasKoNullAnnot(self):
        """ test for methd: has_ko
        """
        null_annot = annot.Annotation("slr0399_synechocystis", [])
        self.failIf(null_annot.has_ko())

    def testHasKoNullAnnot(self):
        """ test for methd: has_ko
        """
        null_annot = annot.Annotation("slr0399_synechocystis", ['K00001',])
        self.assert_(null_annot.has_ko())

    def testIsValidFalseAnnot(self):
        false_annot_null = annot.Annotation("slr0399_synechocystis", [])
        self.failIf(false_annot_null.is_valid())
        false_annot_single_ko = annot.Annotation('hsa:124', [['K00002',], ])
        self.failIf(false_annot_single_ko.is_valid())
        false_annot_multi_kos = annot.Annotation('hsa:124', [['K00001',], ['K00002',] ])
        self.failIf(false_annot_multi_kos.is_valid())

    def testIsValidTrueAnnot(self):
        true_annot_single_ko = annot.Annotation('hsa:124', [['K00001',],])
        self.assert_(true_annot_single_ko.is_valid())

    def testTestKos(self):
        myannot = annot.Annotation('hsa:10020', [['K01791',], ['K00885',]])
        kos = ['K01791', 'K00885']
        self.failUnlessEqual(myannot.get_kos(), kos)

if __name__ == "__main__":
    unittest.main()
