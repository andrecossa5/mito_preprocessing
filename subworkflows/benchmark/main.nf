// measter subworkflow

// Include here
nextflow.enable.dsl = 2
include { SPLIT_BAM } from "../common/modules/split_bam.nf"
include { EXTRACT_FASTA } from "../common/modules/extract_fasta.nf"
include { SAMTOOLS } from "./modules/samtools.nf"
include { COLLAPSE_SAMTOOLS } from "./modules/samtools.nf"
include { CELLSNP } from "./modules/cellsnp_lite.nf"
include { FREEBAYES } from "./modules/freebayes.nf"
include { COLLAPSE_FREEBAYES } from "./modules/freebayes.nf"
include { MAEGATK } from "./modules/maegatk.nf"
include { COLLAPSE_MAEGATK } from "./modules/maegatk.nf"

// 

def processCellBams(cell_bams) {
    return cell_bams
        .map { it ->
            def sample = it[0]
            def paths = it[1]
            return paths.collect { cell_path ->
                def path_splitted = cell_path.toString().split('/')
                def cell = path_splitted[-1].toString().split('\\.')[0]
                return [sample, cell, cell_path]
            }
        }
        .flatMap { it }
}

//

//----------------------------------------------------------------------------//
// benchmark subworkflow
//----------------------------------------------------------------------------//

workflow benchmark {
     
    take:
        ch_bams  

    main:

        EXTRACT_FASTA(params.string_MT)

        if (params.pp_method == "samtools") {

            SPLIT_BAM(ch_bams.map{it->tuple(it[0],it[1])})
            ch_cell_bams = processCellBams(SPLIT_BAM.out.cell_bams)
            SAMTOOLS(ch_cell_bams, EXTRACT_FASTA.out.fasta.map{it->it[0]})
            COLLAPSE_SAMTOOLS(SAMTOOLS.out.calls.groupTuple(by:0))
            ch_output = COLLAPSE_SAMTOOLS.out.allele_counts

        } else if (params.pp_method == "cellsnp-lite") {

            CELLSNP(ch_bams)
            ch_output = CELLSNP.out.ch_output

        } else if (params.pp_method == "freebayes") {

            SPLIT_BAM(ch_bams.map{it->tuple(it[0],it[1])})
            ch_cell_bams = processCellBams(SPLIT_BAM.out.cell_bams) 
            FREEBAYES(ch_cell_bams, EXTRACT_FASTA.out.fasta.map{it->tuple(it[0],it[5])})
            ch_output = COLLAPSE_FREEBAYES(FREEBAYES.out.calls.groupTuple(by:0))

        } else if (params.pp_method == "maegatk") {

            SPLIT_BAM(ch_bams.map{it->tuple(it[0],it[1])})
            ch_cell_bams = processCellBams(SPLIT_BAM.out.cell_bams)
            MAEGATK(ch_cell_bams, EXTRACT_FASTA.out.fasta)
            ch_output = COLLAPSE_MAEGATK(MAEGATK.out.tables.groupTuple(by:0))
        
        } else {
            
            println('Current benchmarking include: maegatk, samtools, cellsnp-lite, freebayes.')
        
        }

    emit:

        ch_output = ch_output

}

//----------------------------------------------------------------------------//