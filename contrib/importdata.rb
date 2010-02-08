#!/usr/bin/env ruby
# Usage: importdata.rb LINKFILE KEGGDB
# Import gene link information in genes_ncbi-geneid.list, genes_ncbi_gi.list, genes_uniprot.list

require 'sqlite3'

f = File.open(ARGV[0])
db = SQLite3::Database.new(ARGV[1])

i=0

db.transaction

begin
  f.each_line do |line|
    i += 1; puts i
    gene, link, other = line.split("\t")
    db.execute("insert into genes_dblinks values (?, ?);", gene, link)
  end
rescue
  db.rollback
end

db.commit
