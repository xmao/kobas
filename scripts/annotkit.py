#!/usr/bin/env python
'''Usage: annotkit  [options] annot_file
Operate anntation file with filters or translator

Mandatory arguments to long options are mandatory for short options too.

    -e EVALUE     evalue cutoff (< EVALUE)
    -i IDENTITY   identity cutoff (>= IDENTITY)
    -o FORMAT     output format, o is original format and t defailed format
                  for all the information
    -r RANK       rank cutoff (<= RANK)
    -s FILE       one-column file with interested sequence IDs
    -t FILE       two-column file with interested source ID and target ID

See annotkit manual or documentation for more information.

Report bug to KOBAS Team  <kobas@mail.cbi.pku.edu.cn>
'''

import re, string
import sys, getopt

from copy import copy
from sets import Set

from kobas import annot
from kobas import config
from kobas import dbutils

class Sieve(Set):
    """ A sieve class, true if stuff in sieve.
    """
    def __init__(self,iterable=None):
        Set.__init__(self,iterable)
        
    def __call__(self,stuff):
        return (stuff.query in self) or False

class Translator(dict):
    """ A translator class, translate id into another form.
    """
    def __init__(self, handle, reverse):
        dict.__init__(self)
        for line in handle:
            ss = line.strip().split('\t')
            if reverse:
                key = ss[1]
                value = ss[0]
            else:
                key = ss[0]
                value = ss[1]
            # process redundant spot, first prior
            if self.has_key(key): continue
            self[key] = value
    
    def __call__(self, old):
        return self[old]

class AnnotTranslator(Translator):

    def __call__(self, old):
        new = copy(old)
        new.query = self[old.query]
        return new

def get_sieve(handle):
    sieve = Sieve()
    for line in handle:
        if line[0] in ['#', '\n']:
            continue
        sieve.add(line.strip())
    return sieve

class XIterator:
    actions = {'sieve':0, 'translator':1}
    
    def __init__(self, iterable):
        self._iter = iterable
        self._hooks = []
        for i in XIterator.actions.keys():
            self._hooks.append([])
    
    def __iter__(self): return self
    
    def register(self, action, func):
        assert(action in XIterator.actions.keys())
        if not callable(func): raise TypeError
        index = XIterator.actions[action]
        self._hooks[index].append(func)

    def is_sieved(self, record):
        sieves = self._hooks[XIterator.actions['sieve']]
        for sieve in sieves:
            if not sieve(record): return False
        return True
                
    def next(self):
        translators = self._hooks[XIterator.actions['translator']]
        while True:
            record = self._iter.next()
            if not self.is_sieved(record): continue
            for translator in translators:
                record = translator(record)
            return record

def is_valid_evalue(record):
    global evalue
    return record.get_evalue() < evalue

def is_valid_rank(record):
    global rank
    return record.get_rank() <= rank

def is_nonil_annot(record):
    return record.olinks != []

def is_valid_similarity(record):
    global similarity
    return record.get_similarity() >= similarity

def usage():
    print >> sys.stderr, __doc__
    sys.exit(1)
    
if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], 'e:hi:o:r:s:t:')
    
    if len(args) != 1:
        usage()
    f = open(args[0], 'r')
    annot_iter = annot.Iterator(f)

    keggdb = dbutils.keggdb()
    # kobasrc = config.getrc()
    
    # evalue = float(kobasrc['evalue'])
    # rank = int(kobasrc['rank'])
    output = 't'
    
    for o, a in opts:
        if o == '-e':
            evalue = float(a)
        elif o == '-i':
            similarity = float(a)
        elif o == '-r':
            rank = int(a)
        elif o == '-o':
            if a == 'o': output = 'o'
        elif o == '-s':
            sieve_file = a
        elif o == "-t":
            trans_file = a
        else: usage()

    xiterator = XIterator(annot_iter)
    xiterator.register('sieve', is_nonil_annot)
    if 'evalue' in dir():
        xiterator.register('sieve', is_valid_evalue)
    if 'rank' in dir():
        xiterator.register('sieve', is_valid_rank)
    if 'similarity' in dir():
        xiterator.register('sieve', is_valid_similarity)
    if 'sieve_file' in dir():
        sieve_fp = open(sieve_file, 'r')
        sieve = get_sieve(sieve_fp)
        xiterator.register('sieve', sieve)
    if 'trans_file' in dir():
        trans_fp = open(trans_file, 'r')
        trans = AnnotTranslator(trans_fp, True)
        xiterator.register('translator', trans)

    if output == 't':
        print "# Cat1\tCat2\tCat3\tKOid\tQuery\tKoname\tEvalue\tRank\tSimilarity"
    for record in xiterator:
        if output == 'o':
            print record
            continue
        else:
            query = record.query
            annot_rank = record.get_rank()
            annot_evalue = record.get_evalue()
            annot_similarity = record.get_similarity()
            koids = record.get_kos()
            paths = keggdb.get_paths(query, koids)
            for path in paths:
                koid = path[3]
                path_str = string.join(map(str, path), '\t')
                koname = keggdb.get_ko_name(koid)
                print '%s\t%s\t%s\t%s\t%s' % \
                      (path_str, koname, annot_evalue, annot_rank, annot_similarity)
