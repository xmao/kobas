#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
# Copyright by Mao Xizeng (maoxz@mail.cbi.pku.edu.cn)
# Created: 2005-04-06 15:04:09
# $Id: kgml.py 465 2008-03-04 18:15:07Z lymxz $

__version__ = '$LastChangedRevision: 465 $'.split()[-2]

"""definition for pathway class
"""
from glob import glob
from os import listdir
from os.path import exists, isdir, join
from types import TypeType
from xml.dom import minidom
from xml.sax import ContentHandler

SUFFIX = 'xml'

class KGMLException(Exception): pass

class ArcheType:                                                   
                                                                  
    def setattrs(obj, attrs, default):                            
        # set attributes with default value                       
        if default in [(), [], {}]:                               
            raise ValueError, '%s not for default value' % default
        for attr in attrs:                                        
            if type(default) == TypeType:                         
                setattr(obj, attr, default())                     
            else:                                                 
                setattr(obj, attr, default)

    def getsattrs(self): return self._sattrs

    def getcattrs(self): return self._cattrs

    def __repr__(self):
        res = ''
        if hasattr(self, '_sattrs'):
            for attr in self._sattrs:
                res += '%s: %s\n' % (attr, getattr(self, attr))
        if hasattr(self, '_cattrs'):
            for attrs in self._cattrs:
                for attr in getattr(self, attrs):
                    res += ''*4 + str(attr)
        return res
    
    __str__ = __repr__ 
                                                                  

class Pathway(ArcheType):

    def __init__(self):
        # set simple attributes with default value 
        self._sattrs = ['name','org','number','title','image','link']
        self.setattrs(self._sattrs, '')
        # set complex attributes with default value
        self._cattrs = ['entries', 'reactions', 'relations']
        self.setattrs(self._cattrs, list)

    def add_entry(self, entry): self.entries.append(entry)

    def add_reaction(self, reaction): self.reactions.append(reaction)

    def add_relation(self, relation): self.relations.append(relation)

    def get_linked_pathways(self):
        linked_pathway_p = lambda entry: entry.type == 'map'
        return filter(linked_pathway_p, self.entries)

    def get_trunk_nodes(self):
        trunk_node_p = lambda entry: entry.map and int(entry.map) > 0
        return filter(trunk_node_p, self.entries)

class Entry(ArcheType):

    def __init__(self):
        self._sattrs = ['id','name','type','link','reaction','map']
        self.setattrs(self._sattrs, '')
        self._cattrs = ['components', 'graphics']
        self.setattrs(self._cattrs, list)

    def add_component(self, component): self.components.append(component)

    def add_graphics(self, graphics): self.graphics.append(graphics)
        

class Component(ArcheType):

    def __init__(self):
        self._sattrs = ['id',]
        self.setattrs(self._sattrs, '')

class Graphics(ArcheType):

    def __init__(self):
        self._sattrs = ['name','x','y','type','width','height','fgcolor','bgcolor']
        self.setattrs(self._sattrs, '')

class Reaction(ArcheType):

    def __init__(self):
        self._sattrs = ['name', 'type']
        self.setattrs(self._sattrs, '')
        self._cattrs = ['substrates', 'products']
        self.setattrs(self._cattrs, list)

    def add_substrate(self, substrate): self.substrates.append(substrate)

    def add_product(self, product): self.products.append(product)

class Reactant(ArcheType):

    def __init__(self):
        self._sattrs = ['name',]
        self.setattrs(self._sattrs, '')


class Relation(ArcheType):

    def __init__(self):
        self._sattrs = ['entry1','entry2','type']
        self.setattrs(self._sattrs, '')
        self._cattrs = ['subtypes',]
        self.setattrs(self._cattrs, list)

    def add_subtype(self, subtype): self.subtypes.append(subtype)
        

class Subtype(ArcheType):

    def __init__(self):
        self._sattrs = ['name', 'value']
        self.setattrs(self._sattrs, '')

factories = {'pathway': Pathway,
            'entry': Entry,
             'component': Component,
             'graphics': Graphics,
             'reaction': Reaction,
             'substrate': Reactant,
             'product': Reactant,
             'relation': Relation,
             'subtype': Subtype,
             }          

##########################################################################################
# class PathwayHandle(ArcheType, ContentHandler):                                        #
#                                                                                        #
#     def __init__(self):                                                                #
#         ContentHandler.__init__(self)                                                  #
#         self._sattrs = ['prev_tag', 'pathway', 'entry','reaction','relation',          #
#                         'component','graphics','substrate','product','subtype']        #
#         self.setattrs(self._sattrs, None)                                              #
#                                                                                        #
#     def startElement(self, name, attrs):                                               #
#                                                                                        #
#         if name == 'pathway':                                                          #
#             # import pdb;pdb.set_trace()                                               #
#             self.pathway = Pathway()                                                   #
#             for k,v in attrs.items():                                                  #
#                 setattr(self.pathway, k, v)                                            #
#         elif name == 'entry':                                                          #
#             self.entry = Entry()                                                       #
#             for k,v in attrs.items():                                                  #
#                 setattr(self.entry, k,v)                                               #
#             self.pathway.entries.append(self.entry)                                    #
#         elif name == 'component':                                                      #
#             self.component = Component()                                               #
#             for k,v in attrs.items():                                                  #
#                 setattr(self.entry, k,v)                                               #
#             self.entry.append(self.component)                                          #
#         elif name == 'graphics':                                                       #
#             self.graphics = Graphics()                                                 #
#             for k,v in attrs.items():                                                  #
#                 setattr(self.entry, k,v)                                               #
#             self.entry.append(self.graphics)                                           #
#                                                                                        #
#     def endElement(self, name):                                                        #
#         if self.prev_tag != name:                                                      #
#             self.prev_tag = name                                                       #
##########################################################################################


class PathwayScanner:
    
#     def __init__(self, reader):
#         self._reader = reader

    def parse(self, filename):
        root = minidom.parse(filename).documentElement
        pathway = Pathway()
        self.setattrs(pathway, root.attributes)
        for child in root.childNodes:
            if child.nodeType == child.ELEMENT_NODE:
                self.handle_element(child, pathway)
        return pathway
                

    def setattrs(self, obj, attrs):
        for k,v in attrs.items():
            setattr(obj, k, v)

    def factory(self, name): return factories[name]

    def handle_element(self, element = None, parent = None):
        obj = self.factory(element.nodeName)()
        self.setattrs(obj, element.attributes)
        for child in element.childNodes:
            if child.nodeType == child.ELEMENT_NODE:
                self.handle_element(child, obj)
        add_method = getattr(parent, 'add_%s' % element.nodeName)
        add_method(obj)

def pathways_from_dir(dir_):
    pathways = {}
    parser = PathwayScanner()
    try:
        for fname in glob(join(dir_, '*.%s' % SUFFIX)):
            path = parser.parse(fname)
            pathways[path.name] = path
    except:
        raise KGMLException
    return pathways

class kgml:

    def __init__(self, location):
        if not isdir(location):
            raise KGMLException, "Not a valid kgml directory"
        self.location = location

    def get_pathways(self, org):
        if not self.verify_org(org):
            raise KGMLException, "%s: not a valid organism" % org
        return pathways_from_dir(join(self.location,org))

    def get_orgs(self):
        dirs = []
        for dir_ in listdir(self.location):
            if isdir(join(self.location, dir_)):
                dirs.append(dir_)
        return dirs

    def verify_org(self, org):
        dir_ = join(self.location, org)
        return exists(dir_) and isdir(dir_)

    

if __name__ == "__main__":
    import sys
    ps = PathwayScanner()
    pathway = ps.parse(sys.argv[1])
    print pathway
