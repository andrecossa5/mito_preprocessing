// SEARCH_PATTERNS module

nextflow.enable.dsl = 2

//

process SEARCH_PATTERNS {

  label 'scLT'
    
  output:
  path "search_patterns.tsv", emit: search_patterns

  script:
  """
  python \
  ${baseDir}/bin/bulk_gbc/generate_search_patterns.py ${params.lenti_pattern}
  """

  stub:
  """
  touch search_patterns.tsv
  """

}
