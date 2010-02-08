"""test cases of knode class in ktree module"""

import unittest
from kobas.ktree import KNode

class TestQueryKNode(unittest.TestCase):

    def setUp(self):
        self.root = KNode('A', None, {})
        self.root.addChild('B')
        self.root.addChild('C')
        self.root['B'].addChild('E')
        self.root['B'].addChild('F')
        self.root['C'].addChild('D')
        self.root['C'].addChild('E')
        self.root['C']['D'].addChild('G')
        
    def testIsSibling(self):
        b = self.root['B']
        c = self.root['C']
        self.assert_(b.isSibling(b))
        self.assert_(b.isSibling(c))
        self.assert_(c.isSibling(b))

    def testIsChild(self):
        b = self.root['B']
        e = self.root['B']['E']
        self.assert_(b.isChild(self.root))
        self.assert_(e.isChild(b))

    def testIsLeaf(self):
        b = self.root['B']
        self.failIf(b.isLeaf())
        e = self.root['B']['E']
        self.assert_(e.isLeaf())
        g = self.root['C']['D']['G']
        self.assert_(e.isLeaf())

    def testEqual(self):
        
        a1 = KNode('A', None, {})
        a2 = KNode('A', None, {})
        self.assertEqual(a1, a2)
        
        b1 = KNode('B', None, {})
        self.assertNotEqual(a1,b1)

        b = self.root['B']
        c = self.root['C']
        self.assertNotEqual(b, c)

        e1 = self.root['B']['E']
        e2 = self.root['C']['E']
        self.assertEqual(e1, e2)

    # def testGetChild():

if __name__ == "__main__":
    unittest.main()
