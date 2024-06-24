// GATHER_ALLELIC_TABLES module

nextflow.enable.dsl = 2

process GATHER_TABLES {

    tag "${sample}"

    input:
    tuple val(sample), path(files)

    output:
    tuple val(sample), 
          path("T_allelic_tables_cell.tsv.gz"), 
          path("G_allelic_tables_cell.tsv.gz"),
          path("A_allelic_tables_cell.tsv.gz"), 
          path("C_allelic_tables_cell.tsv.gz"),
          path("coverage_allelic_tables_cell.tsv.gz"), 
          emit: tables

    script:
    """
    #!/bin/bash
    
    for ext in T G A C coverage; do
        touch "\${ext}_cells.txt"
    done
    bash ${baseDir}/bin/maester/process_files.sh \${files}
    echo 'prova'
    
    for ext in T G A C coverage; do
        sed 's/,/\t/g' \${ext}_cells.txt > \${ext}_allelic_tables_cell.tsv
        gzip --fast \${ext}_allelic_tables_cell.tsv
    done
    """



    stub:
    """
    for ext in "T" "G" "A" "C" "coverage"; do
        touch "\${ext}_allelic_tables_cell.tsv.gz"
    done
    """
}