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
  fgbio -Xmx8g --compression 0 --async-io GroupReadsByUmi \
    --input ${cell}.bam   \
    --strategy ${params.fgbio_UMI_consensus_mode} \
    --edits ${params.fgbio_UMI_consensus_edits}   \
    --output grouped.bam  \
    -t UB \
    -T MI \

  fgbio -Xmx4g --compression 0 CallMolecularConsensusReads \
    --input grouped.bam \
    --output /dev/stdout \
    --min-reads ${params.fgbio_min_reads}  \
    --min-input-base-quality ${params.fgbio_base_quality}
    --threads 4 \
    |  fgbio -Xmx8g --compression 1 FilterConsensusReads \
        --input /dev/stdin \
        --output filtered_consensus.bam\
      --ref ${params.ref}/cassette_up.fa   \
      --min-reads ${params.fgbio_min_reads}  \
      --min-base-quality ${params.fgbio_base_quality} \
      --max-base-error-rate ${params.fgbio_base_error_rate}

  samtools fastq filtered_consensus.bam \
    | bwa mem -t 16 -p -K 150000000 -Y ${params.ref} - \
    | fgbio -Xmx4g --compression 0 --async-io ZipperBams \
        --unmapped filtered_consensus.bam \
        --ref ${params.ref} \
        --tags-to-reverse Consensus \
        --tags-to-revcomp Consensus \
    | samtools sort -@ 1 -o ${cell}_consensus_filtered_mapped.bam --write-index

  """

  stub:
  """
  touch ${cell}_consensus_filtered_mapped.bam
  """

}