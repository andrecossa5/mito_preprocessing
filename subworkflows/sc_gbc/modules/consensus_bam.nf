// CONSENSUS_BAM module

nextflow.enable.dsl = 2

//

process CONSENSUS_BAM {

  tag "${sample_name}: ${cell}"

  input:
  tuple val(sample_name), val(cell), path(bam)

  output:
  tuple val(sample_name), val(cell), path("${cell}_consensus_filtered_mapped.bam"), emit: consensus_filtered_bam

  script:
  """

  #...

  """

  stub:
  """
  touch ${cell}_consensus_filtered_mapped.bam
  """

}

