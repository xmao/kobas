#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
# Copyright by Mao Xizeng (maoxz@mail.cbi.pku.edu.cn)
# Created: 2005-01-08 09:57:34
# $Id: TestDiscover.py 504 2008-05-30 00:49:59Z lymxz $

__version__ = '$LastChangedRevision: 504 $'.split()[-2]

"""unittest for discovery.py
"""

import os, unittest
from sets import Set

from Cheetah.Template import Template

from kobas import config, discover, exception, tests

class TestTwoSampleTest(unittest.TestCase):

    def testInitFalse(self):
        sample1 = []
        sample2 = []
        sample3 = []
        self.failUnlessRaises(TypeError, discover.TwoSampleTest, sample1)
        self.failUnlessRaises(TypeError,
                              discover.TwoSampleTest, sample1, sample2, sample3)

    def testGetProb(self):
        dist = discover.Dist()
        dist['red'] = 5
        dist['white'] = 4
        dist['black'] = 8
        dist['green'] = 3
        mybinom = discover.BinomTest(discover.Dist(), discover.Dist())
        self.failUnlessEqual(mybinom.get_prob(dist, 'red'), 0.25)
        self.failUnlessEqual(mybinom.get_prob(dist, 'orange'), 0)

    def testFdr(self):
        sample1 = discover.dist_from_distfile(
            tests.get_test_data('synechocystis'))
        sample2 = discover.dist_from_distfile(
            tests.get_test_data('s.cerevisiae'))
        mybinom = discover.BinomTest(sample1, sample2)
        result = mybinom()
        result.fdr()
        self.failUnlessEqual(len(result[0]), 7)

class TestDist(unittest.TestCase):

    def testAdd(self):
        dist = discover.Dist()
        dist.add('1', 1)
        testres = Set()
        testres.add(1)
        self.failUnlessEqual(dist['1'], testres)
        dist.add('1', 1)
        self.failUnlessEqual(dist['1'], testres)

    def testUpdate(self):
        dist = discover.Dist()
        for i in range(10):
            dist['a'] = i
        dist.update('b', range(10))
        self.failUnlessEqual(dist['a'], dist['b'])

        dist.update('c', range(10))
        dist.update('c', range(5, 15))
        dist.update('d', range(15))
        self.failUnlessEqual(dist['c'], dist['d'])

    def testSize(self):
        dist = discover.Dist()
        dist.update('a', range(50))
        dist.update('b', range(25,75))
        dist.update('c', range(100, 200))
        self.failUnlessEqual(dist.size(), len(range(75))+len(range(100,200)))

    def testGetProb(self):
        dist = discover.Dist()
        dist.update('a', range(50))
        dist.update('b', range(25,75))
        dist.update('c', range(100, 200))
        prob = float(50)/175
        self.failUnlessEqual(dist.get_prob('a'), prob)


    def testFromFile(self):
        dist = discover.dist_from_annot_file(
            tests.get_test_data('test_annot.txt'))
        self.failUnlessEqual(dist.size(), 278)

class TestStatistics(unittest.TestCase):

    def testHyper(self):
        q,m,n,k = 5, 50, 800, 90
        self.failUnlessEqual(
            discover.hyper(q,m,n,k), 1-discover.rpy.r.phyper(q-1,m,n,k))

    def testBinom(self):
        m,n,p = 1, 2, 0.5
        self.failUnlessEqual(discover.binom(m, n, p), 0.75)

    def testIsValidpValue(self):
        tdata = [i * 0.1 for i in range(1,11)]
        self.failUnless(discover.is_valid_pvalue(tdata))
        fdata = [float('nan'), -0.1, 2]
        for val in fdata:
            self.failIf(discover.is_valid_pvalue([val]))

    def testChisqTest(self):
        data = [[254,246], [219,281]]
        self.failUnlessAlmostEqual(discover.chisq_test(*data), 0.0312801)

class TestCheetah(unittest.TestCase):

    def testCheetah(self):
        tmpl = os.path.join(config.getrc()['kobas_home'], 
                            "template", "test_html.tmpl")
        data = {'thead':range(7), 'result':[range(7) for i in range(10)], 'title':'Test'}
        t = Template(file=tmpl, searchList=[data,])
        self.failUnless(str(t).find('$') == -1)


if __name__ == "__main__":
    unittest.main()
