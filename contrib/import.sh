#!/usr/bin/env sh

# 
sqlite3 kegg.dat < ../data/kegg.sql

#
./importgenome.rb genome kegg.dat

#
./importko.rb ko kegg.dat

#
mkdir -p gene_dist
cd gene_dist
../generatedist.rb ../ko ../kegg.dat
cd -

#
for i in *.list; do
    ./importdata.rb $i kegg.dat
done
