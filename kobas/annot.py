"""Annotate sequences with KO terms"""

from Bio.Blast import NCBIStandalone, NCBIXML

import config, dbutils, ktree

class Annotation(object):
    """association with koes for query gene,
    olink a list of kos (ko,rank,evalue,score,identitiy)
    """

    def __init__(self,query,olinks):
        # assert query != None and olinks isinstance(types.TupleType)
        self.query=query
        self.olinks=olinks

    def get_evalue(self):
        if self.olinks:
            return float(self.olinks[0][2])
        else:
            return None

    def get_rank(self):
        if self.olinks:
            return int(self.olinks[0][1])
        else:
            return None

    def get_score(self):
        if self.olinks:
            return float(self.olinks[0][3])
        else:
            return None

    def get_similarity(self):
        if self.olinks:
            return float(self.olinks[0][4])
        else:
            return None

    def get_kos(self):
        """ get all KO Objects from the database according olinks
        """
        if self.olinks:
            return [olink[0] for olink in self.olinks]
        else:
            return []

    def get_paths(self):
        """ get all paths from ko top level to query
        """
        mykeggdb = dbutils.keggdb()
        return mykeggdb.get_paths(self.query, self.get_kos())
    
    def _getko_by_id(self,ko_id):
        """ get KO record from the database according to ko_id
        """
        return ko_id

    def has_ko(self):
        """ Check if the gene have KO association.
        """
        return len(self.olinks) != 0

    def is_valid(self):
        """ Is I valid according to kg table, true if all ko is valid
        """
        mykeggdb = dbutils.keggdb()
        if not self.get_kos():
            return False
        else:
            for ko_id in self.get_kos():
                if not mykeggdb.is_valid_annot((self.query, ko_id)):
                    return False
        
        return True

    def __str__(self):
        s = ''
        if len(self.olinks)>0:
            for olink in self.olinks:
                solink = map(str,olink)
                s += ' ' + ':'.join(solink)
            s.lstrip()
        return '%s\t%s' % (self.query, s)

    def __repr__(self):
        return self.__str__()

def parse_annot(line):
    """ extract query and KO entries from line
    format: query\tko_id:rank:evalue:score:identitiy ...
    """
    olinks = []

    l = line.strip().split('\t')
    query = l[0]

    if len(l) == 2:
        for annot in l[1].split():
            olinks.append(annot.split(':'))
    return Annotation(query, olinks)

def is_annot_comment(line):
    return line[0] in '#\n'

def is_annot(line):
    return not is_annot_comment(line)

class Iterator(object):

    def __init__(self, handle):
        self._handle = handle

    def __iter__(self): return self

    def next(self):
        while True:
            line = self._handle.next()
            if is_annot(line):
                return parse_annot(line)

def annots2ktree(ss):
    """return a list of annots into a ktree, "KO" is root
    """
    root = ktree.KNode('KO', None, {})
    ss = filter(is_annot, ss)
    for s in ss:
        annot = parse_annot(s)
        if annot.olinks:
            root.addPaths(annot.get_paths())
    return root

class Reader(object):

    def __iter__(self):
        raise NotImplementedError

class Selector(object):

    def select(self, record):
        raise NotImplementedError

class Annotator(object):

    def __init__(self, reader, selector):
        self.reader, self.selector = reader, selector

    def annotate(self, verbose=True):
        for record in self.reader:
            # Very weird, NCBIStandalone returns None without record
            if not record: break
            yield self.selector.select(record)

class BlastOutputReader(object):

    def __init__(self, handle, format=7):
        self.handle = handle
        self.format = int(format)
    
    def __iter__(self):
        return NCBIXML.parse(self.handle)

class BlastProgReader(BlastOutputReader):

    def __init__(self, blastcmd, program, database, infile, **kargs):
        if 'align_view' in kargs:
            kargs.pop('align_view')
        blastout, blasterr = NCBIStandalone.blastall(
            blastcmd, program, database, infile, **kargs)
        BlastOutputReader.__init__(self, blastout)

class BlastSelector(object):
    
    def __init__(self, keggdb, **kargs):
        self.keggdb, self.cutoffs = keggdb, kargs

    def select(self,record):
        """ Give a blast record, select a valid alignment according to evalue and rank"""
        ret, rank = Annotation(record.query.split()[0], []), 1
        for alignment in record.alignments:
            if rank > self.cutoffs['rank'] or \
                   alignment.hsps[0].expect > self.cutoffs['evalue']:
                break
            # TODO: KEGG Fasta format conflicts NCBI Fasta format: headline is identified by
            #       BLAST as definition, no id :-/
            hit = alignment.title.startswith('gnl|') \
                  and alignment.hit_def.split()[0] or alignment.hit_id
            ko_ids = self.keggdb.get_kos_by_gene(hit)
            if ko_ids:
                evalue = alignment.hsps[0].expect
                score = alignment.hsps[0].score
                identity = float(alignment.hsps[0].identities) / alignment.hsps[0].align_length
                for ko_id in ko_ids:
                    ret.olinks.append((ko_id, rank, evalue, score, identity, hit))
                return ret
            rank += 1
        return ret

class IdMapReader(file):

    DBS = {
        'ncbigene' : 'ncbi-geneid',
        'ncbigi' : 'ncbi-gi',
        'uniprot' : 'up',
    }
    
    def __init__(self, name, db='', **kargs):
        file.__init__(self, name, **kargs)
        self.db = db  

    def next(self):
        line = file.next(self).strip()
        if self.db:
            return '%s:%s' % (self.DBS[self.db], line)
        else:
            return line

class IdMapSelector(Selector):

    def __init__(self, keggdb):
        self.keggdb = keggdb

    def select(self, record):
        "record: dbname:seqid, like ncbi-geneid:10008"
        return Annotation(record, zip(self.keggdb.get_kos_by_dblink(record)))
