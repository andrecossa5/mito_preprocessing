nextflow.enable.dsl = 2

// Include here
include { bulk_gbc } from "../bulk_gbc/main"
include { tenx } from "../tenx/main"
include { tenx_merged } from "../tenx/main"
include { sc_gbc } from "../sc_gbc/main"
include { get_tenx_gbc_bam } from "../get_bam/main"
include { get_gbc_bam } from "../get_bam/main"
include { get_gbc_bam_merged } from "../get_bam/main"
include { SPLIT_MIXED_FASTQ } from "../common/modules/split_mixed_fastq.nf"
include { SEARCH_PATTERNS } from "../bulk_gbc/modules/generate_search_patterns.nf"


//


// Build the pre-processing channel from the input sample sheet (params.input_sheet, a CSV).
// The layout of the sheet depends on params.input_type, which selects the pipeline entry point:
//
//   "fastq"      -> Start from raw, unaligned reads (10x + GBC libraries).
//                   Columns: sample, fastq_folder, library
//                   ('library' must be TENX or GBC; TENX reads are aligned, GBC reads
//                    are matched to the resulting cell barcodes).
//
//   "fastq,GBC"  -> Start from raw, unaligned GBC reads only, with an external set of
//                   already-called cell barcodes.
//                   Columns: sample, fastq_folder, cell_barcodes (.txt of valid 10x barcodes)
//
//   "bam"        -> Start from previously aligned reads, with an external set of cell barcodes.
//                   Columns: sample, bam, cell_barcodes (.txt of valid 10x barcodes)
//
//   "fastq,mixed" -> Start from raw, unaligned reads where the TENX and GBC libraries are
//                    mixed within the same FASTQs. Reads are merged and split by library
//                    (on the R2 lentiviral anchor), then processed as in "fastq".
//                    Columns: sample, fastq_folder
//
// Any other value of params.input_type raises an error.
def createPreprocessingChannel() {

    if (params.input_type == "fastq") {

        // From raw reads, unaligned
        ch = Channel.fromPath(params.input_sheet)
            .splitCsv(header: true)
            .map { row -> [ row.sample, row.fastq_folder, row.library ] }
        
    } else if (params.input_type == "fastq,GBC") {

        // From raw reads, unaligned (GBC) and a .txt file of valid 10x barcodes
        ch = Channel.fromPath(params.input_sheet)
            .splitCsv(header: true)
            .map { row -> [ row.sample, row.fastq_folder, row.cell_barcodes ] }
        
    } else if (params.input_type == "bam") {

        // From aligned reads, and a .txt file of valid 10x barcodes
        ch = Channel.fromPath(params.input_sheet)
            .splitCsv(header: true)
            .map { row -> [ row.sample, row.bam, row.cell_barcodes ] }

    } else if (params.input_type == "fastq,mixed") {

        // From raw reads, unaligned, with TENX and GBC libraries mixed in the same FASTQs
        ch = Channel.fromPath(params.input_sheet)
            .splitCsv(header: true)
            .map { row -> [ row.sample, row.fastq_folder ] }
    }
    else {
        error "Unsupported input_type: ${params.input_type}. Available: \"fastq\", \"fastq,GBC\", \"bam\", or \"fastq,mixed\"."
    }
    return ch
}


//


//----------------------------------------------------------------------------//
// tenx_gbc subworkflow
//----------------------------------------------------------------------------//

workflow tenx_gbc {

    take:
        ch

    main:
    
        // Handle different input types
        if (params.input_type == "fastq") {

            // All 10x and GBC reads
            tenx_fastqs = ch.filter{it->it[2]=='TENX'}.map{it->tuple(it[0],it[1])}
            gbc_fastqs = ch.filter{it->it[2]=='GBC'}.map{it->tuple(it[0],it[1])}
            tenx(tenx_fastqs)
            get_tenx_gbc_bam(gbc_fastqs, tenx.out.cell_barcodes)
            ch_filtered = get_tenx_gbc_bam.out.tenx_bam

        } else if (params.input_type == "fastq,GBC") {

            // GBC reads
            gbc_fastqs = ch.map{it->tuple(it[0],it[1])}
            cell_barcodes = ch.map{it->tuple(it[0],it[2])}
            get_gbc_bam(gbc_fastqs, cell_barcodes)
            ch_filtered = get_gbc_bam.out.gbc_bam

        } else if (params.input_type == "bam") {

            // Previously aligned reads
            ch_filtered = ch

        } else if (params.input_type == "fastq,mixed") {

            // TENX and GBC reads mixed in the same FASTQs: split by library (reads are
            // already merged by SPLIT_MIXED_FASTQ), then as in "fastq" without re-merging.
            // GBC reads are matched to the lentiviral anchor with up to 1 mismatch, reusing
            // the bulk SEARCH_PATTERNS wildcard patterns.
            SEARCH_PATTERNS()
            SPLIT_MIXED_FASTQ(ch, SEARCH_PATTERNS.out.search_patterns.first())
            tenx_merged(SPLIT_MIXED_FASTQ.out.tenx)
            get_gbc_bam_merged(SPLIT_MIXED_FASTQ.out.gbc, tenx_merged.out.cell_barcodes)
            ch_filtered = get_gbc_bam_merged.out.gbc_bam

        }

        // Fire sc_gbc subworkflow
        sc_gbc(ch_filtered)
    
    emit:
        summary = sc_gbc.out.summary_json

}

//----------------------------------------------------------------------------//
