"""Wrapper for database operations."""

import copy, sys, string

if sys.version_info >= (2,5):
    import sqlite3 as sqlite
else:
    try:
        from pysqlite2 import dbapi2 as sqlite
    except ImportError:
        raise ImportError("pysqlite2 module (http://code.google.com/p/pysqlite/) desn't exist, please install")

from kobas import config

class keggdb:
    """a simple class wrapper to kegg database
    """
    def __init__(self, dbfile="", *args, **kwargs):
        """ init a keggdb object
        """
        if dbfile:
            self.db = sqlite.connect(dbfile, *args, **kwargs)
        else:
            self._rc = config.getrc()
            self.db = sqlite.connect(self._rc['keggdb'], *args, **kwargs)
        self.cursor = self.db.cursor()

    def execsql(self, sql, *args):
        """ execute sql statement, return all result through a list
        """
        self.cursor.execute(sql, args)
        return self.cursor.fetchall()

    def get_species_abbr(self, name):
        return self.execsql(
            "select abbr from species where name = ?;", name)[0][0]
    
    def get_species_name(self, abbr):
        return self.execsql(
            "select name from species where abbr = ?;", abbr)[0][0]
           
    def get_kos_by_gene(self, gene_id):
        "get all koids mapped to geneid"
        sql = "select ko_id from kos_genes where gene_id = ?;"
        return [ item[0] for item in self.execsql(sql, gene_id) ]
    
    def get_kos_by_dblink(self, dblink_id):
        sql = """select distinct ko_id from kos_genes, genes_dblinks
            where kos_genes.gene_id = genes_dblinks.gene_id 
            and genes_dblinks.dblink_id = ?;"""
        return [ i[0] for i in self.execsql(sql, dblink_id) ]
        
    def get_ko3s(self, koid):
        """ get all the third level terms of the koid
        """
        sql = "select distinct cat3 from kos where ko_id = ?;"
        return [ item[0] for item in self.execsql(sql, koid) ]

    def get_paths(self, query, kos):
        """ get all paths (all level terms) from ko table
        """
        res = []
        
        paths = self.execsql(
            'select cat1,cat2,cat3,pathway_id,ko_id from kos where ko_id in ?;', kos)

        if kos:
            for path in paths:
                # print path, type(path)
                res.append((path[0], path[1], "%s [%s]" % (path[2], path[3]), path[4], query))
        else:
            return []

        return res

    def get_ko_name(self, koid):
        "get the name owning to ko entry."
        sql = "select distinct name from kos where ko_id = ?;"
        return self.execsql(sql, koid)[0][0]
    

    def get_gnome_size(self, organism):
        sql = """select count(gene_id) from
        (select distinct gene_id from kos_genes where gene_id like '%%_%s');""" % organism
        return self.execsql(sql)[0][0]

    def ko3term2pathwayid(self, ko3term):
        "return pathway id by cat3 term, generally one by one."
        sql = "select distinct pathway_id from kos where cat3 = ?;"
        return self.execsql(sql, ko3term)[0][0]

    def is_valid_annot(self, annot):
        """ Sig.: (gene_id, ko_id) -> boolean
        Method: Is an tupple of annotation is valid, true in table kg, or false not in kg
        """
        if len(annot) == 2:
            gene_id, ko_id = annot[0], annot[1]
        else:
            gene_id, ko_id = annot[0], ''
        sql = "select count(*) from kos_genes where gene_id = ? and ko_id = ?;"
        return self.execsql(sql, gene_id, ko_id)[0][0] > 0

    def is_valid_gene_id(self, gene_id):
        """ Sig.: str -> boolean
        Method: Is the gene_id valid, true if in kg, false not
        """
        sql = "select count(*) from kos_genes where gene_id = ?;"
        return self.execsql(sql, gene_id)[0][0] > 0
