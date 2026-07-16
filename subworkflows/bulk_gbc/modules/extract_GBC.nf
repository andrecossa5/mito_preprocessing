// EXTRACT_GBC module

nextflow.enable.dsl = 2

//

process EXTRACT_GBC {

  label 'scLT'
  tag "${sample_name}"

  input:
  tuple val(sample_name), val(in_folder)
  path search_patterns

  output:
  tuple val(sample_name), path('GBC_not_corrected.tsv'), emit: GBC

  script:
  """
  # lenti_start is 0-based (as in consensus_tsv.py); awk substr() is 1-based, hence the + 1
  zcat ${in_folder}/*_R1_*.fastq.gz ${in_folder}/*_R2_*.fastq.gz | \
  awk 'NR % 4 == 2' | \
  egrep -f ${search_patterns} -o | \
  awk '{print substr(\$0, ${params.lenti_start} + 1, ${params.lenti_bc_length});}' \
  > GBC_not_corrected.tsv
  """

  stub:
  """
  touch GBC_not_corrected.tsv
  """
  
}
