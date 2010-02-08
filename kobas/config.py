#!/usr/bin/env python
"""environment variables for program"""
import os, sys, string
import ConfigParser
                                                                                          
def getrc():
    """ return KOAS resource dictionary
    """
    rc = krc()

    if os.environ.has_key('HOME'):
        rcfg_file = os.environ['HOME'] + "/.kobasrc"
    else:
        rcfg_file = ""
    rcbg_file = '/etc/kobasrc'

    rcfg_filep = os.access(rcfg_file, os.F_OK)
    rcbg_filep = os.access(rcbg_file, os.F_OK)
    
    if rcfg_filep and rcbg_filep:
        return rc.merge(rcfg_file, rcbg_file)
    elif rcbg_filep:
        return rc.read(rcbg_file)
    elif rcfg_filep:
        return rc.read(rcfg_file)
    else:
        print "Error: configuration not exist."
        sys.exit(1)


class krc:
    """ KOAS esource file parser
    """
    _sections  = {'DEFAULT':[('kobas_home','/usr/share/kobas'),
                             ('blast_home','/usr/bin')],
                  'KEGG':[('keggdb','%(dat_dir)s/data/keggdb.dat'), ],
                  'BLAST':[('blast','%(blast_home)s/blastall'),
                           ('blastdb','%(blast_home)s/data/keggseq.fasta')],
                  'PARAMETER':[('evalue','1.0e-5'),
                               ('rank','5')]}

    def create(self,rcfile):
        """ create resource file from scratch
        """
        import copy
        rcparser = ConfigParser.ConfigParser()
        sections = copy.deepcopy(krc._sections)

        for sec,kvars in sections.items():
            if (sec != "DEFAULT") and (not rcparser.has_section(sec)):
                rcparser.add_section(sec)
            for kvar,kvalue in kvars:
                rcparser.set(sec,kvar,kvalue)
        rcparser.write(open(rcfile,'w'))

    def read(self,rcfile):
        """ return a dict of all resources
        """
        res = {}
        rcparser = ConfigParser.ConfigParser()
        rcparser.read(rcfile)
        
        for option,value in rcparser.defaults().items():
            res[option] = value
	    
        for section in rcparser.sections():
            for option in rcparser.options(section):
                res[option] = rcparser.get(section,option)
        
        return res

    def write(self, rcfile, option, value):
        """ set option to new value, which can affect future operation
        """
        rcparser = ConfigParser.ConfigParser()
        rcparser.read(rcfile)

        if option in rcparser._defaults.keys():
            rcparser.set('DEFAULT',option,value)

        for section in rcparser.sections():
            if rcparser._sections[sections].has_key(option):
                rcparser.set(section, option, value)
                rcparser.write(rcfile,'w')
                return True

        print "No option"
        sys.exit(1)

    def merge(self, rcfile_fg, rcfile_bg):
        """ merge rcfile_fg and rcfile_bg,
        with the options in rcfile_fg overriding rcfile_bg
        """
        rc_fg = self.read(rcfile_fg)
        rc_bg = self.read(rcfile_bg)

        # for key in rc_fg.keys():
        #     if not rc_bg.has_key(key):
        #         print 'Error: your kobasrc profile exist invalid keywords'
        #         sys.exit(1)
        rc_bg.update(rc_fg)
        return rc_bg

context = getrc()

if __name__ == "__main__":
    import pprint
    pprint.pprint(getrc())
