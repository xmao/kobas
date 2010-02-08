"""Wrapper for database operations."""

import copy, sys, string

from pysqlite2 import dbapi2 as sqlite

from kobas import config

def sql_normalize(s):
    """ Translate "'" in str into "\'", and wrap str with two "'".
    """
    return norm(s)

def norm(s):
    """ Translate "'" in str into "''", and wrap str with two "'".
    """
    ns = s.replace("'",r"''")
    return wrap_str(ns)

def wrap_str(s,deli="'"):
    """ wrap a str with double "\'".
    """
    return wrap(s)

def wrap(s,deli="'"):
    """ wrap a string with deli character
    """
    return "%s%s%s" % (deli,s,deli)

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
            self.db = sqlite.connect(self._rc['kobasdb'], *args, **kwargs)
        self.cursor = self.db.cursor()

    def execsql(self, sql):
        """ execute sql statement, return all result through a list
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_species_abbr(self, name):
        sql = "select abbr from species where name = '%s';" % name
        return self.execsql(sql)[0][0]
    
    def get_species_name(self, abbr):
        sql = "select name from species where abbr = '%s';" % abbr
        return self.execsql(sql)[0][0]
           
    def get_kos_by_gene(self, gene_id):
        """ get all koids mapped to geneid
        """
        sql = "select ko_id from kos_genes where gene_id = '%s';" % gene_id
        return [item[0] for item in self.execsql(sql)]
    
    def get_kos_by_dblink(self, dblink_id):
        sql = """select distinct ko_id from kos_genes, genes_dblinks
            where kos_genes.gene_id = genes_dblinks.gene_id 
            and genes_dblinks.dblink_id = '%s';""" % dblink_id
        return [ i[0] for i in self.execsql(sql) ]
        
    def get_ko3s(self, koid):
        """ get all the third level terms of the koid
        """
        sql = "select distinct cat3 from kos where ko_id='%s';" % koid
        return [item[0] for item in self.execsql(sql)]

    def get_paths(self, query, kos):
        """ get all paths (all level terms) from ko table
        """
        res = []
        
        wrap_kos = map(lambda s: r"'%s'" % s,kos)
        str_kos = '(' + string.join(wrap_kos,',') + ')'
        sql = """select cat1,cat2,cat3,pathway_id,ko_id from kos
        where ko_id in %s;""" % str_kos
        paths = self.execsql(sql)

        if kos:
            for path in paths:
                # print path, type(path)
                res.append((path[0], path[1], "%s [%s]" % (path[2], path[3]), path[4], query))
        else:
            return []

        return res

    def get_ko_name(self, koid):
        """ get the name owning to ko entry.
        """
        res = ""
        sql = "select distinct name from kos where ko_id='%s';" % koid
        return self.execsql(sql)[0][0]
    

    def get_gnome_size(self, organism):
        """
        """
        sql = """select count(gene_id) from
        (select distinct gene_id from kos_genes where gene_id like '%%_%s');""" % organism
        return self.execsql(sql)[0][0]

    def ko3term2pathwayid(self, ko3term):
        """return pathway id by cat3 term, generally one by one.
        """
        sql = """select distinct pathway_id from kos where cat3=%s;""" % norm(ko3term)
        pathwayid = self.execsql(sql)[0][0]
        return pathwayid!='ot00000' and pathwayid or ''

    def is_valid_annot(self, annot):
        """ Sig.: (gene_id, ko_id) -> boolean
        Method: Is an tupple of annotation is valid, true in table kg, or false not in kg
        """
        gene_id = annot[0]

        if len(annot) == 1:
            ko_id = ''
        elif len(annot) == 2:
            ko_id = annot[1]
        else:
            print "Wrong annotation"
            sys.exit(1)
            
        sql = """select count(*) from kos_genes where gene_id = '%s' and ko_id = '%s';""" \
              % (gene_id, ko_id)

        return self.execsql(sql)[0][0] > 0

    def is_valid_gene_id(self, gene_id):
        """ Sig.: str -> boolean
        Method: Is the gene_id valid, true if in kg, false not
        """
        sql = """select count(*) from kos_genes where gene_id = '%s';""" % gene_id
        return self.execsql(sql)[0][0] > 0
        
        
    def insert(self, sql):
        """ insert query with data modified
        """
        try:
            self.cursor.execute(sql)
        except NameError:
            print "insert error!!!"
            print "the sql is: %s" % sql
            sys.exit(status=1)

    def insert_ko(self, ko_id, name, definition,
                  cat1='', cat2='', cat3='', pathway_id=''):
        """ insert ko information into ko table
        """
        sql = """ INSERT INTO kos VALUES \
        (%s, %s, %s, %s, %s, %s, %s);""" % \
        (ko_id, name, definition, cat1, cat2, cat3, pathway_id)
        self.insert(sql)

    def insert_kg(self, ko_id, gene_id):
        """
        """
        sql = """ INSERT INTO kos_genes VALUES \
        (%s, %s);""" % (ko_id, gene_id)
        self.insert(sql)
        
