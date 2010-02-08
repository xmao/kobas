CREATE TABLE 'genes_dblinks' (
    gene_id varchar(50) not null,
    dblink_id varchar(50) not null
);
CREATE TABLE 'kos' (
       ko_id char(6) not null,
       name text,
       definition text,
       cat1 text,
       cat2 text,
       cat3 text,
       pathway_id char(7)
);
CREATE TABLE 'kos_dblinks' (
       ko_id char(6) not null,
       dbname text not null,
       dbid text not null
);
CREATE TABLE 'kos_genes' (
       ko_id char(6) not null,
       gene_id varchar(50) not null
);
CREATE TABLE species (
       abbr varchar(10) not null,
       name varchar(500) not null
);
CREATE INDEX genes_dblinks_index_dblink on genes_dblinks (dblink_id);
CREATE INDEX genes_dblinks_index_gene on genes_dblinks (gene_id);
CREATE INDEX kos_dblinks_index_koid on 'kos_dblinks' (ko_id);
CREATE INDEX kos_genes_index_gene on kos_genes (gene_id);
CREATE INDEX kos_genes_index_koid on kos_genes (ko_id);
CREATE INDEX kos_index_koid on kos (ko_id);
CREATE INDEX species_index_abbr on species (abbr);
CREATE INDEX species_index_name on species (name);

