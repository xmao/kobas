#!/usr/bin/env ruby
# Usage: generatedists.rb KOFILE
# Create gene distributions from the aspect of pathway, one file per genome

require 'set'
require 'sqlite3'
require 'bio/io/flatfile'
require 'bio/db/kegg/orthology'

db, abbrs = SQLite3::Database.new(ARGV[1]), {}
db.execute("select abbr, name from species;") do |abbr,name|
  abbrs[abbr] = name
end

kos, orgs = Bio::FlatFile.open(Bio::KEGG::ORTHOLOGY, ARGV[0]), {}

kos.each do |ko|
  puts ko.entry_id
  pathways = []
  ko.keggclasses.each do |class_|
    pathways.push(class_.split('; ')[2])
  end
  ko.genes.each do |o,genes|
    next if not abbrs.has_key?(o.downcase)
    org = abbrs[o.downcase]
    
    if not orgs.has_key?(org)
      orgs[org] = {}
    end
    
    pathways.each do |pathway|
      if not orgs[org].has_key?(pathway)
        orgs[org][pathway] = Set.new
      end
      orgs[org][pathway].merge(genes)
    end
  end
end

puts orgs

orgs.each do |org,pathways|
  file = File.new(org, 'w')
  pathways.each do |pathway,genes|
    file.puts("#{ pathway }\t#{ genes.to_a.join(',') }")
  end
  file.close()
end
