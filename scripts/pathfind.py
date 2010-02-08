#!/usr/bin/python
""" find enriched pathways by frequency of terms or statistical significance of
terms.  Certain abbreviation (3 chars) can be designated to indicate any genome
in KEGG GENES, so any user defined file name shoulded be larger than 3 chars.
"""

__doc__ = '''
Usage: pathfind [options] fgfile [bgfile ...]
Discover the most frequent or enriched pathways

Mandatory arguments to long options are mandatory for short options too.

   -h          Show this help
   -k METHOD   Choose statistical method, b is binomial test, c is chi square
               method and h is hypergeometric test. Default is hypergeometric
               test.
   -n          Disable FDR correction
   -o FORMAT   Output format, h is html and t is flat text.  Default is text.

See pathfind manual page for more information.

Report bug to KOBAS Team <kobas@mail.cbi.pku.edu.cn>
'''

import os, sys
import getopt, string

from kobas import config
from kobas import dbutils
from kobas import discover
from kobas import exception

dist_tab = {'b':'BinomTest', 'c':'ChiTest', 'h':'HyperTest'}

def get_dist(alias):
    assert(alias in dist_tab.keys())
    return getattr(discover, dist_tab[alias])

def get_tilte(alias):
    return 'The most enriched pathways based on %s' % dist_tab[alias]

def get_output(result, out_type, title='Output'):
    if out_type == 'h':
        return result.to_html(title)
    else:
        return str(result)

def find_path(dist_type, samdist, bgdist):
    """ find significant terms of sample from backgroud distribution
    dist_type: distribution abbr.,  binomial, chisq, hypergemetry available
    samdist: {term:amount}, sample distribution
    bgdist: {term:amount}, background distribution
    """
    dist_class = get_dist(dist_type)
    dist = dist_class(samdist, bgdist)
    return dist()

def arg2dist(arg):
    """ get dist dict in term of arg, abbrev for genome or used defined annot
    """
    kobasrc = config.getrc()
    if len(arg) == 3:
        keggdb = dbutils.keggdb()
        distfile = os.path.join(
            kobasrc["kobas_home"], "gene_dist",
            keggdb.get_species_name(arg.lower()))
        dist_dict = discover.dist_from_distfile(open(distfile))
    else:
        if not os.access(arg, os.F_OK):
            print "File: %s not exist" % arg
            sys.exit(0)
        dist_dict = discover.dist_from_annot_file(open(arg, 'r'))
    dist_size = dist_dict.size()
    return (dist_dict, dist_size)

def opt2dict(opts):
    """ opts [(o, a), ...]
    """
    res = {}
    for o,a in opts:
        res[o] = a
    return res

def usage():
    """ print help of pathfind.py
    """
    print >> sys.stderr, __doc__

def error(s):
    print 'Error: '+s+'\n'

if __name__ == "__main__":

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hk:no:')
    except:
        error('Usage')
        usage()
        sys.exit(1)

    # process command options
    dopts = opt2dict(opts)
    output_type = dopts.get('-o', 't')
    test_type = dopts.get('-k', 'h')
    if test_type not in 'bch' or output_type not in 'ht':
        usage()
        sys.exit(1)

    if len(args) == 0 or ('-h', '') in opts:
        usage()
        sys.exit(1)
    elif len(args) == 1:
        dist, size = arg2dist(args[0])
        res = discover.TestResult(['Pathway', 'Count'])
        for pathway, genes in dist.items(): res.add_row([pathway, len(genes)])
        res.sort(order=1)
        print get_output(res, output_type, 'The Most Frequent Pathways')
    elif len(args) == 2:
        samdist, samsize = arg2dist(args[0])
        bgdist, bgsize = arg2dist(args[1])
        
        # Do statistical computation
        try:
            res = find_path(test_type, samdist, bgdist)
        except ArithmeticError, msg:
            exception.error(msg)
            sys.exit(1)
        
        # Do FDR correction
        if not dopts.has_key('-n'):
            try:
                res.fdr()
            except ArithmeticError, msg:
                exception.error(msg)
                res.sort(key=-1)
            else:
                res.sort(key=-2)
        else:
            res.sort(key=-1)
        
        print get_output(res, output_type, get_tilte(test_type))
