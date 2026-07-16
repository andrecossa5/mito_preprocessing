// SPLIT_MIXED_FASTQ module

nextflow.enable.dsl = 2

//

// Merge all lanes and split a mixed-library folder of paired-end FASTQs into
// separate TENX and GBC read sets, in a single streaming pass over the data.
// A read pair is assigned to GBC when its R2 sequence matches the lentiviral anchor
// with up to 1 mismatch; otherwise it is assigned to TENX. The 1-mismatch match
// reuses the wildcard patterns produced by the bulk SEARCH_PATTERNS process (one
// pattern per anchor position, that position replaced by a regex wildcard).
// Each split is emitted as a folder holding merged R1/R2, so it can be consumed
// by the existing folder-based tenx() / get_tenx_gbc_bam() subworkflows.

process SPLIT_MIXED_FASTQ {

  label 'scLT'
  tag "${sample_name}"

  input:
  // in_folder: the sample's mixed-library FASTQs (any number of lanes). R1 reads hold
  // the 16 bp cell barcode + 12 bp UMI; R2 reads hold either cDNA (TENX) or the
  // lentiviral cassette + GBC (GBC). R1/R2 lanes are matched by the *R1*/*R2* globs.
  tuple val(sample_name), val(in_folder)
  // search_patterns: one wildcard regex per line (from bulk SEARCH_PATTERNS), matching
  // the anchor with up to 1 mismatch; combined into a single alternation for the split.
  path search_patterns

  output:
  // Each emit is a folder of merged R1/R2 for one library, split by the R2 anchor:
  //   tenx -> reads WITHOUT the anchor (10x cDNA)         -> tenx/R1.fastq.gz, tenx/R2.fastq.gz
  //   gbc  -> reads WITH the anchor (lentiviral GBC)      -> gbc/R1.fastq.gz,  gbc/R2.fastq.gz
  // Both files always exist (empty gzip if the sample has only one read type).
  tuple val(sample_name), path("tenx"), emit: tenx
  tuple val(sample_name), path("gbc"),  emit: gbc

  script:
  """
  mkdir -p tenx gbc

  paste <(pigz -dc ${in_folder}/*R1*.fastq.gz) <(pigz -dc ${in_folder}/*R2*.fastq.gz) \
  | paste - - - - \
  | awk -F'\\t' -v patfile="${search_patterns}" '
      BEGIN {
        while ((getline line < patfile) > 0) {
          if (line == "") continue
          regex = (regex == "" ? line : regex "|" line)
        }
      }
      {
        if (\$4 ~ regex) {
          print \$1"\\n"\$3"\\n"\$5"\\n"\$7 | "pigz -p ${task.cpus} > gbc/R1.fastq.gz"
          print \$2"\\n"\$4"\\n"\$6"\\n"\$8 | "pigz -p ${task.cpus} > gbc/R2.fastq.gz"
        } else {
          print \$1"\\n"\$3"\\n"\$5"\\n"\$7 | "pigz -p ${task.cpus} > tenx/R1.fastq.gz"
          print \$2"\\n"\$4"\\n"\$6"\\n"\$8 | "pigz -p ${task.cpus} > tenx/R2.fastq.gz"
        }
      }'

  # Guarantee all outputs exist even if a sample has reads of a single type
  for f in tenx/R1 tenx/R2 gbc/R1 gbc/R2; do
    [ -f \$f.fastq.gz ] || : | pigz > \$f.fastq.gz
  done
  """

  stub:
  """
  mkdir -p tenx gbc
  touch tenx/R1.fastq.gz tenx/R2.fastq.gz gbc/R1.fastq.gz gbc/R2.fastq.gz
  """

}
