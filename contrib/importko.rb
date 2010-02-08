#!/usr/bin/env ruby
# Usage: importko.rb KOFILE KEGGDB
# Import all information in original KO file into SQLite 3 backend database.

require 'sqlite3'
require 'bio/io/flatfile'
require 'bio/db/kegg/orthology'

kos = Bio::FlatFile.open(Bio::KEGG::ORTHOLOGY, ARGV[0])
db = SQLite3::Database.new(ARGV[1])

# Put all insert statements in a transaction, which dramatically speed up
db.transaction

begin
  kos.each do |entry|
    puts entry.entry_id
    
    if entry.keggclasses.length == 0
      db.execute("insert into kos values (?, ?, ?, '', '', '', '');",
                 entry.entry_id, entry.name, entry.definition)
    else
      entry.keggclasses.each_index do |i|
        cat1, cat2, cat3 = entry.keggclasses[i].split('; ')
        pid = entry.pathways[i]
        db.execute("insert into kos values (?, ?, ?, ?, ?, ?, ?);", 
                   entry.entry_id, entry.name, entry.definition, cat1, cat2, cat3, pid)
      end
    end
    
    entry.genes.each do |org, genes|
      genes.each do |gene|
        db.execute("insert into kos_genes values (?, ?);", entry.entry_id, "%s:%s" % [org, gene])
      end
    end
  end
rescue
  db.rollback
end

db.commit
