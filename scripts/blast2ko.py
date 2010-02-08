#!/usr/bin/env python
"""Annotate a set of sequences with KEGG Orthology, blastp for protein, blastx
for amino acid."""

import sys,string

from optparse import OptionParser
from Bio.Blast import NCBIStandalone

from kobas import annot
from kobas import config
from kobas import dbutils
from kobas import exception
from kobas import fasta
from kobas import ktree

def config_option():
    """ configure options and arguments for blast2ko.py
    """
    usage = """%prog [-e evalue] [-g graph_output_file] [-r rank] [-p blast_program] [-t]
     datafile (fasta file of proteins)"""
    
    p = OptionParser(usage)
    p.add_option(
        "-e", "--evalue", dest="evalue", action="store", 
        type="string", help="expect cutoff for BLAST, default 1e-5")
    p.add_option(
        "-i", "--intype", dest="intype", default="fasta", action="store", type="string", 
        help="input type (fasta, blastout, seqids), default fasta; can specify db by the format \
 of 'seqids:db' from (%s) when using seqids option" % ', '.join(annot.IdMapReader.DBS.keys()))
    p.add_option(
        "-n", "--nprocessors", dest="nprocessors", default=1, action="store",
        type="int", help="specify how many CPUs to use by blast, default 1"),
    p.add_option(
        "-p", "--program", action="store", dest="blast_prog", default="blastp",
        help="specify which program to use by blastall, default blastp")
    p.add_option(
        "-r", "--rank", dest="rank", action="store", type="string", 
        help="rank cutoff for valid hit from BLAST, default 5")
    (opt,args) = p.parse_args()
    return (p,opt,args)
    
if __name__ == "__main__":
    opt_parser,opt,args = config_option()

    if len(args) != 1:
        opt_parser.print_help()
        sys.exit(1)

    # Blast environment configuration
    kobasrc = config.getrc()

    # Integrate command line switches into environments
    if opt.rank:
        kobasrc["rank"] = opt.rank
    if opt.evalue:
        kobasrc["evalue"] = opt.evalue

    keggdb = dbutils.keggdb(kobasrc['kobasdb'])
    
    if opt.intype == "fasta":
        # verify fasta file
        try:
            try:
                f = open(args[0])
                fasta.verify(f)
            finally:
                f.close()
        except exception.FastaIOError, msg:
            exception.error(msg)
            sys.exit(1)
        annotator = annot.Annotator(
            reader = annot.BlastProgReader(
                kobasrc['blast'], opt.blast_prog, kobasrc['blastdb'], args[0],
                align_view='7', nprocessors=opt.nprocessors),
            selector = annot.BlastSelector(
                keggdb, evalue=float(kobasrc['evalue']), rank=int(kobasrc['rank'])))
    elif opt.intype == 'blastout':
        annotator = annot.Annotator(
            reader = annot.BlastOutputReader(open(args[0])),
            selector = annot.BlastSelector(
                keggdb, evalue=float(kobasrc['evalue']), rank=int(kobasrc['rank'])))
    elif opt.intype == 'seqids':
        annotator = annot.Annotator(
            reader = annot.IdMapReader(args[0]),
            selector = annot.IdMapSelector(keggdb))
    elif opt.intype.startswith('seqids:'):
        db = opt.intype.split(':')[1]
        annotator = annot.Annotator(
            reader = annot.IdMapReader(args[0], db),
            selector = annot.IdMapSelector(keggdb))
    else:
        sys.exit('%s input is not supported yet, only fasta, blastout, seqids' % opt.intype)

    annots = dict([ (i.query, i) for i in annotator.annotate() ])
    
    # Report annotation result
    num_gene_has_ko,num_gene_no_ko = 0,0
    for annot in annots.values():
        if annot.has_ko():
            num_gene_has_ko += 1
        else:
            num_gene_no_ko += 1

    if opt.intype in ('fasta', 'blastout'):
        print "# Method: BLAST\tCondition: expect <= %s; rank <= %s" % (kobasrc['evalue'], kobasrc['rank'])
        print "# Summary:\t%d succeed, %d fail" % (num_gene_has_ko,num_gene_no_ko)
        print "\n# query\tko_id:rank:evalue:score:identity"
    elif opt.intype.startswith('seqids'):
        print "# Method: Id mapping\tCondition: rank <= %s" % kobasrc['rank']
        print "# Summary:\t%d succeed, %d fail" % (num_gene_has_ko,num_gene_no_ko)
        print "\n# query\tko_id:rank:hit"
        
    
    for annot in annots.values():
        annotstr = str(annot)
        if opt.intype.startswith('seqids:'):
            print annotstr[(annotstr.find(':')+1):]
        else:
            print annotstr
