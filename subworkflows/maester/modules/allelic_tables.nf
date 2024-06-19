// ALLELIC_TABLES module

nextflow.enable.dsl = 2

//

process ALLELIC_TABLES {

  tag "${sample_name}: ${cell}"

  input:
  tuple val(sample_name), val(cell), path(bam)

  output:
  tuple val(sample_name), 
    val(cell), 
    path("${cell}.A.txt"),
    path("${cell}.C.txt"),
    path("${cell}.T.txt"),
    path("${cell}.G.txt"), 
    path("${cell}.coverage.txt"), emit: allelic_tables

  script:
  """
  python ${baseDir}/bin/maester/make_allelic_tables.py \
  --input_bam ${bam} \
  --cell ${cell} \
  --min_base_qual ${params.fgbio_base_quality} \
  --min_alignment_quality ${params.min_alignment_quality}

  """

  stub:
  """
  touch ${cell}.A.txt"
  touch ${cell}.C.txt"
  touch ${cell}.T.txt"
  touch ${cell}.G.txt"
  touch ${cell}.coverage.txt"

  """

}

