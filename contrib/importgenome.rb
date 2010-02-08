#!/usr/bin/env ruby
# User: importgenome.rb GENOMEFILE KEGGDB
# Import species abbreviation and full name into species in keggseq.dat

require 'sqlite3'
require 'bio/io/flatfile'
require 'bio/db/kegg/genome'

genomes = Bio::FlatFile.open(Bio::KEGG::GENOME, ARGV[0])
db = SQLite3::Database.new(ARGV[1])

db.transaction

begin
  genomes.each do |genome|
    db.execute("insert into species values (?, ?);", genome.entry_id, genome.name.split(',')[0])
  end
rescue
  db.rollback
end

db.commit
