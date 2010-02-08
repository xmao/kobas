"utilities to manipulate fasta file"

from os.path import join
from types import InstanceType

from Bio import SeqIO

from exception import FastaIOError

def verify(handle, level=0):
    try:
        for rec in SeqIO.parse(handle, 'fasta'):
            # capture the error of only one title without sequence
            # at the end of fasta file, ignoring blank lines at the end.
            # Just some temporary solutions
            if rec.seq.data == '' or rec.id == '':
                raise FastaIOError
    except Exception, args:
        seq = locals().get('rec', 'the first')
        if seq.id:
            label = locals().get('rec', 'the first').id
            msg = 'Bad fasta format at " the FIRST " sequence'
        else:
            label = '\n%s\n' % str(seq)
            msg = 'Bad fasta format after " %s " sequence' % label
        msg += """\n
Possible reasons:\n
- Illegal Fasta format\n
- If you input sequence IDs, forget to choose proper database type.\n
"""
        raise FastaIOError, msg
