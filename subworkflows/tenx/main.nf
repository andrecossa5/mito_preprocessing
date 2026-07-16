// sc_pp workflow

// Include here
nextflow.enable.dsl = 2
include { MERGE_R1 } from "../common/modules/merge_R1.nf"
include { MERGE_R2 } from "../common/modules/merge_R2.nf"
include { SOLO } from "../common/modules/Solo.nf"

// 

process publish_tenx {

    label 'scLT'
    tag "${sample_name}"

    // Publish
    publishDir "${params.outdir}/${sample_name}/", mode: 'copy'

    input:
        tuple val(sample_name),
              path(raw),
              path(filtered),
              path(stats), 
              path(summary),
              path(bam)

    output:
        path(raw)
        path(filtered)
        path(stats)
        path(summary)

    script:
    """
    echo moving everything to ${params.outdir}
    """
    stub:
        """
        # make raw/ with dummy files
        mkdir -p raw
        touch raw/dummy1.fq.gz raw/dummy2.fq.gz

        # make filtered/ with dummy files
        mkdir -p filtered
        touch filtered/barcodes.tsv.gz
        touch filtered/matrix.mtx.gz
        touch filtered/features.tsv.gz

        # other standalone outputs
        touch Features.stats
        touch Summary.csv
        touch Aligned.sortedByCoord.out.bam
        """
}

// 


//----------------------------------------------------------------------------//
// tenx subworkflow
//----------------------------------------------------------------------------//


workflow tenx {

    take:
        ch_input

    main:
    
        MERGE_R1(ch_input)
        MERGE_R2(ch_input)
        SOLO(MERGE_R1.out.R1.combine(MERGE_R2.out.R2, by:0))
        publish_input = SOLO.out.raw
            .combine(SOLO.out.filtered, by:0)
            .combine(SOLO.out.stats, by:0)
            .combine(SOLO.out.summary, by:0)
            .combine(SOLO.out.bam, by:0)
        publish_tenx(publish_input)

    emit:

        cell_barcodes = SOLO.out.cell_barcodes
        filtered = SOLO.out.filtered

}


//----------------------------------------------------------------------------//
// tenx_merged subworkflow
//   Same as tenx(), but the input is a folder that already holds merged R1/R2
//   (e.g. from SPLIT_MIXED_FASTQ), so SOLO is called directly without re-merging.
//----------------------------------------------------------------------------//


workflow tenx_merged {

    take:
        ch_input   // tuple(sample_name, merged_folder) with R1.fastq.gz + R2.fastq.gz

    main:

        reads = ch_input.map { sample_name, folder ->
            tuple(sample_name, file("${folder}/R1.fastq.gz"), file("${folder}/R2.fastq.gz"))
        }
        SOLO(reads)
        publish_input = SOLO.out.raw
            .combine(SOLO.out.filtered, by:0)
            .combine(SOLO.out.stats, by:0)
            .combine(SOLO.out.summary, by:0)
            .combine(SOLO.out.bam, by:0)
        publish_tenx(publish_input)

    emit:

        cell_barcodes = SOLO.out.cell_barcodes
        filtered = SOLO.out.filtered

}


//----------------------------------------------------------------------------//