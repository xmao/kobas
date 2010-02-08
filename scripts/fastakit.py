#!/usr/bin/env python
'''Usage: fastakit [options] fasta_file
Manipulate fasta-format sequence file with filter or translator

Mandatory arguments to long options are mandatory for short options too.

    -s FILE    one-column file with interested sequence IDs
    -t FILE    two-column file with interested source ID and target ID

See fastakit manual or documentation for more information.

Report bug to KOBAS Team <kobas@mail.cbi.pku.edu.cn>
'''

import sys, os
from copy import copy
from sets import Set
from Bio import Fasta

class FastaSelectiveIterator(Fasta.Iterator):
    """a seletive iterator on fasta file.
    """
    
    def __init__(self, filter, handle, parser = None, debug = 0):
        
        Fasta.Iterator.__init__(self,handle, parser, debug)
        self._filter = filter

    def get_id(self, title):
        return title.split()[0]
        
    def next(self):

        while True:
            rec = Fasta.Iterator.next(self)
            if rec == None:
                return None
            elif self._filter(self.get_id(rec.title)):
                rec.title = self.get_id(rec.title)
                return rec
            else:
                continue

class Sieve(Set):
    """ A sieve class, true if stuff in sieve.
    """
    def __init__(self,iterable=None):
        Set.__init__(self,iterable)
        
    def __call__(self,stuff):
        if stuff in self:
            return True
        return False

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

class FastaTranslator(Translator):
    """ A Fasta record translator, translator one record to another.
    """

    def __init__(self, handle, reverse = False):
        Translator.__init__(self, handle, reverse)

    def __call__(self, old_record):
        new_record = copy(old_record)
        new_record.title = self[old_record.title]
        return new_record
    

def get_sieve(handle):
    """
    """
    sieve = Sieve()
    
    for line in handle:
        if line[0] in ['#', '\n']:
            continue
        sieve.add(line.strip())
    
    return sieve

def usage():
    print >> sys.stderr, __doc__

def get_input_handle(file_name):
    if file_name == '-':
        return sys.stdin
    else:
        return open(file_name, 'r')

if __name__ == "__main__":

    import getopt
    
    opts, args = getopt.getopt(sys.argv[1:], 'hs:t:')

    if not opts or len(args) != 1:
        usage()
        sys.exit('Error usage')

    fasta_file = open(args[0])
    parser = Fasta.RecordParser()
    
    for o, a in opts:
        if o == '-h':
            usage()
            sys.exit(0)
        elif o == '-s':
            sieve = get_sieve(get_input_handle(a))
            iterator = FastaSelectiveIterator(sieve, fasta_file, parser)
            for record in iterator:
                print record
        elif o == '-t':
            translator = FastaTranslator(get_input_handle(a), reverse = True)
            iterator = Fasta.Iterator(fasta_file, parser)
            for record in iterator:
                print translator(record)
        else:
            usage()
            sys.exit('Error usage')
