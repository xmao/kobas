#!/usr/bin/env sh
# dump.sh DATADIR DUMPDIR
# Dump all kobas data out for release

DATADIR=${1:-.}
DUMPDIR=${2:-kobas-data}

# Create directories
mkdir -p $DUMPDIR/db $DUMPDIR/fasta $DUMPDIR/static

# Dump out kegg.dat
echo "Dumping SQLite database ... OK :-)"
sqlite3 $DATADIR/kegg.dat '.dump' > $DUMPDIR/db/kegg-dump.sql

# Dump out keggseq.fasta
echo "Dumping fasta sequences ... OK :-)"
cp $DATADIR/keggseq.fasta $DUMPDIR/fasta/

# Dump out gene distribution in ko groups
echo "Dumping static files ... OK :-)"
cp -r $DATADIR/gene_dist/ $DUMPDIR/static/
cp -r $DATADIR/template/ $DUMPDIR/static/

echo "Your data have been dumped into kobas-data directory, and you can tar and publish it now."