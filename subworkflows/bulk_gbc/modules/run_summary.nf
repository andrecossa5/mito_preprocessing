// generate_run_summary_bulk module

nextflow.enable.dsl = 2

//

// Process
process generate_run_summary_bulk {

  tag "${sample_name}"

  input:
  tuple val(sample_name), path(raw_counts)
  tuple val(sample_name), path(corrected_counts)
  tuple val(sample_name), path(correction_df)

  output:
  tuple val(sample_name), path('run_summary.txt'), emit: summary

  script:
  """
  python \
  ${baseDir}/bin/bulk_gbc/create_run_summary.py \
  --indir ${params.bulk_gbc_indir} \
  --outdir ${params.bulk_gbc_outdir} \
  --anchor_sequence ${params.bulk_gbc_anchor_sequence} \
  --sample ${sample_name} \
  --raw_counts ${raw_counts} \
  --corrected_counts ${corrected_counts} \
  --correction_df ${correction_df} \
  --min_n_reads ${params.bulk_gbc_min_n_reads} \
  --hamming_treshold ${params.bulk_gbc_graph_clustering_hamming_treshold} 
  """

  stub:
  """
  touch run_summary.txt
  """

}