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

  fgbio GroupReadsByUmi -i ${bam} -o ${cell}_grouped.bam -s ${params.fgbio_UMI_consensus_mode}  -e ${params.fgbio_UMI_consensus_edits} -t UB -T MI
  fgbio CallMolecularConsensusReads -t UB -i ${cell}_grouped.bam  -o ${cell}_consensus_unmapped.bam   -M ${params.fgbio_min_reads}

  samtools fastq ${cell}_consensus_unmapped.bam \
    | bwa mem -t 16 -p -K 150000000 -Y ${params.ref}/cassette_up.fa - \
    | fgbio --compression 1 --async-io ZipperBams --unmapped ${cell}_consensus_unmapped.bam  \
      --ref ${params.ref}/cassette_up.fa  \
      --tags-to-reverse Consensus \
      --tags-to-revcomp Consensus \
      --output ${cell}_consensus_mapped.bam 

  fgbio -Xmx8g --compression 0 FilterConsensusReads \
    --input ${cell}_consensus_mapped.bam \
    --output /dev/stdout \
    --ref ${params.ref}/cassette_up.fa  \
    --min-reads ${params.fgbio_min_reads} \
    --min-base-quality ${params.fgbio_base_quality} \
    --max-base-error-rate ${params.fgbio_base_error_rate} \
  | samtools sort -@ ${task.ncpus} -o ${cell}_consensus_filtered_mapped.bam --write-index

  """

  stub:
  """
  touch ${cell}_consensus_filtered_mapped.bam
  """

}

