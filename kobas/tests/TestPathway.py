"""unittest class for kegg pathway parser"""

import unittest

from os.path import join, exists, isdir

from kobas.tests import get_test_data_dir
from kobas.pathway import pathway_from_files, pathlist_from_dir, pathways_from_dir

dirname = join(get_test_data_dir(), 'pathway')
pathname = 'aae00252'

class TestPathway(unittest.TestCase):

    def testData(self):
        self.failUnless(exists(dirname) and isdir(dirname))

    def testPathwayFromFiles(self):
        pathway = pathway_from_files(pathname, dirname)
        self.failUnlessEqual(len(pathway.linked_pathways()), 16)
        self.failUnlessEqual(len(pathway.orthologs()), 26)
        self.failUnlessEqual(len(pathway.genes()), 14)
        self.failUnlessEqual(len(pathway.compounds()), 13)
        self.failUnlessEqual(len(pathway.reactions()),13)

    def testPathListFromDir(self):
        self.failUnlessEqual(len(pathlist_from_dir(dirname)), 2)

    def testPathwaysFromDir(self):
        self.failUnlessEqual(len(pathways_from_dir(dirname).keys()), 2)

if __name__ == "__main__":
    unittest.main()
