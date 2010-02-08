#!/usr/bin/env python
# Copyright by Mao Xizeng (maoxz@mail.cbi.pku.edu.cn)
# Created: 2004-07-25 10:39:26
# $Id: ktree.py 465 2008-03-04 18:15:07Z lymxz $

__version__ = '$LastChangedRevision: 465 $'.split()[-2]

"""KO Hierarchy Tree based on Python Normal Dictionary
"""

class KNode:
    """ Node in the KO Hierarchy Tree, default 5 levels.
    root: parent: None
    leaf: children: []
    """

    def __init__(self,desc,parent,children):
        """Sig.: str, KNode(None),dict({}) -> None
        Method: initialize a KNode
        Usage:
               root = KNode('A',None,{})
               a = KNode('B',root,{})   # also, root.addChild('B')
        """
        self.desc = desc
        self.parent = parent
        self.children = children
    
    def isSibling(self,aknode):
        """Sig.: KNode -> boolean
        Method: are self and aknode siblings?
        Usage:
               root = KNode('A',None,{})
               root.addChildren(('B','C')) # A->B
                                           # |->C
               root['B'].isSibling(root['C']) # True
        """
        if aknode.parent is None or self.parent is None:
            return False
        return self.parent is aknode.parent
    
    def isChild(self,aknode):
        """Sig.: KNode -> boolean
        Method: is self a child of aknode?
        Usage: root = KNode('A',Node,{})
               root.addChild('B')       # A -> B
               root['B'].isChild(root)  # True
        """
        return self in aknode.children.values()

    def isLeaf(self):
        """Sig.: None -> boolean
        Method: leaf or intermediate node
        Usage:
               root = KNode('A', None, {})
               root.addChildren(('B'), 'C')
               root.isLeaf()            # false
               root['B'].isLeaf()       # true
        """
        return self.children == {}
        

    def getChildren(self):
        """Sig.: Null -> list
        Method: return a list of children
        Usage: children = root.getChildren() # [...]
               print children
        """
        return self.children.values()

    def getChild(self,name):
        """Sig.: str -> KNode
        Method: return the KNode whose key is name
        Usage: tmp = root.getChild('B') # also root['B']
               print children        
        """
        if self.children.has_key(name):
            return self.children[name]
        return None

    def addChild(self,child):
        """Sig.: str -> KNode
        Method: add a child, return the recently added obj
        Usage: root = KNode('A',Node,{})
               root.addChild('B')       # A -> B
        """
        achild = KNode(child,self,{})
        self.children[achild.desc] = achild
        return achild
        
    def addChildren(self,children):
        """Sig.: iterable -> None
        Method: add a list of children
        Usage: root = KNode('A',None,{})
               root.addChildren(('B','C')) # A->B
                                           # |->C
        """
        for child in children.values():
            self.addChild(self,child,self)

    def getLeaves(self):
        """Sig: () -> Set
        Method: return all leaf nodes
        Usage: root = KNode('A', None, {})
               root.addPath(('B','C','D'))
               root.addPath('E','F')
               print root.getLeaves()   # Set([D,F])]
        """
        res = Leaves()
        self.traverse(res)
        return res.leaves
    
    def getEdges(self):
        res = []
        if self.children != {}:
            for child in self.children.values():
                res.append((str(self), str(child)))
        return res
    
    def getDepth(self):
        """ Sig: () -> int
        Method: get the depth of aknode
        """
        return len(self.getPath())-1
    
    def getPath(self):
        """Sig.: () -> []
        Method: return a path to root node.
        Usage: root = KNode('A',None,{})
               root.addChildren(('B','C'))
               c = root['C']
               print c.getPath()
        """
        aknode = self
        path = [self]
        while aknode:
            path.append(aknode)
            aknode = aknode.parent
        path.reverse()
        return path
        

    def addPath(self,path):
        """Sig.: [] -> None
        Method: add a path into ktree, self as root node
        Usage: root = KNode('A',None,{})
               root.addPath(['B','C','D','E'])
               root.addpath(['F','G'])  # A->B->C->D->E
                                        # |->F->G
        """
        if len(path)>0:
            if self.children.has_key(path[0]):
                node = self.children[path[0]]
            else:
                node = self.addChild(path[0])
            node.addPath(path[1:])
            
    def addPaths(self,paths):
        """Sig.: [Path] -> None
        Method: add a list of paths into a tree, self as root node
        Usage: root = KNode('A',None,{})
               root.addPath([['B','C','D','E'],
                             ['F','G']])  # A->B->C->D->E
                                          # |->F->G
        """
        if len(paths)>0:
            for path in paths:
                self.addPath(path)
    
    def getAncestor(self,aknode):
        """Sig.: KNode -> KNode
        Method: get common ancestor of self and aknode
        Usage: root = KNode('A',None,{})
               root.addChildren(('B','C'))
               b = root['B']
               c = root['C']
               b.getAncestor(c)         # return root
        """
        minpath = self.getPath()
        maxpath = aknode.getPath()
        if len(minpath)>len(maxpath):
            minpath,maxpath = maxpath,minpath
        for node in minpath:
            if node in maxpath:
                return node

    def traverse(self, visitor):
        """ Sig.: callable -> visitor(aknode)
        Method: traverse ktree, whose root is self
        Usage: root = KNode('A',None,{})
               root.addChildren(('B','C'))
               root.traverse(print_knode)
        """
        visitor(self)
        if self.children != {}:
            for child in self.children.values():
                child.traverse(visitor)
        
    def __str__(self):
        if self.isLeaf():
            return self.desc
        else:
            return '%s (%d)' % (self.desc, len(self.getLeaves()))

    def __repr__(self):
        return self.__str__()

    def __eq__(self, aknode):
        """ Sig.: KNode -> boolean
        Method: retrun true if the desc of the two knodes are equal, or false
        """
        return self.desc == aknode.desc
    
    def __ne__(self,aknode):
        return not self.__eq__(aknode)

    def __getitem__(self,key):
        """Sig.: str -> KNode
        Method: return a child with the key
        Usage: \troot['B']                # return a obj whose key is 'B'
               root['C']
        """
        return self.children[key]
    
def print_knode(aknode):
    """Sig.: KNode -> None
    Usage: aknode.traverse(print_knode)
    Func: recursely print a KTree according to respective depth
    """
    if aknode.getDepth() > 0:
        s = "|  "*(aknode.getDepth()-1) + "|--" + str(aknode)
        print s
    elif aknode.getDepth() == 0:
        print aknode

def draw_knode(aknode,outfile=''):
    """draw a pretty figure of a knode
    """
    import sets,pydot
    edges = Edges()
    aknode.traverse(edges)

    g = pydot.graph_from_edges(edges.edges)
    g.add_node(pydot.Node(name='node',color='lightblue2',style='filled'))
    g.parent_graph.type = 'digraph'
    if outfile == '':
        g.write_jpeg('graph_output.jpg', prog='dot')
    else:
        g.write_jpeg(outfile, prog='dot')


class Edges:
    """ Class: a callback class, a state visitor 
    Usage: edgs = Edges()
           aknode.traverse(edgs)
           print edgs.edges
    """
    def __init__(self):
        import sets
        self.edges=sets.Set()
    def __call__(self,aknode):
        self.edges.update(aknode.getEdges())

class Leaves:
    """ Class: a callback class, a state visitor
    Usage: leaves = Leaves()
           aknode.traverse(leaves)
           print leaves
    """
    def __init__(self):
        import sets
        self.leaves = sets.Set()

    def __call__(self, aknode):
        if aknode.children == {}:
            self.leaves.add(aknode.desc)
        return self.leaves


if __name__ == '__main__':
    execfile('/etc/pythonrc')
    root = KNode('A',None,{})
    root.addChild('B')
    root.addChild('C')
    root['B'].addChild('E')
    root['B'].addChild('F')
    root['C'].addChild('D')
    b = root['B']
    c = root['C']
    vtr = Edges()
    root.traverse(vtr)
    root.traverse(print_knode)
