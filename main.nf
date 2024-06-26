// mi_to_preprocessing, working
nextflow.enable.dsl = 2

// Include here
include { bulk_gbc } from "./subworkflows/bulk_gbc/main"
include { tenx } from "./subworkflows/tenx/main"
include { sc_gbc } from "./subworkflows/sc_gbc/main"
include { maester } from "./subworkflows/maester/main"


//




// Create folders
process CREATE_FOLDER {

    input:
        tuple val(path_source), val(name_new_path_bulk), val(id_we_want)

    output:
        tuple val(name_new_path_bulk), path(name_new_path_bulk), emit: samples

    script:
    """ 
    mkdir -p ${name_new_path_bulk}
    cd ${name_new_path_bulk}
    ln -s ${path_source}/${name_new_path_bulk}/*R2_*.fastq.gz .
    ln -s ${path_source}/${name_new_path_bulk}/*R1_*.fastq.gz .



    """

    stub:
    """
    mkdir -p ${name_new_path_bulk}

    """

}


//


// (Bulk DNA) targeted DNA sequencing of GBC
// ch_bulk_gbc = Channel
//     .fromPath("${params.bulk_gbc_indir}/*", type:'dir') 
//     .map{ tuple(it.getName(), it) }
//     
// // GBC enrichment from 10x library
// ch_sc_gbc = Channel
//     .fromPath("${params.sc_gbc_indir}/*", type:'dir')
//     .map{ tuple(it.getName(), it) }
// 
// // 10x GEX library
// ch_tenx = Channel
//     .fromPath("${params.sc_tenx_indir}/*", type:'dir')
//     .map{ tuple(it.getName(), it) }
// 
// // MAESTER library
// ch_maester = Channel
//     .fromPath("${params.sc_maester_indir}/*", type:'dir') 
//     .map{ tuple(it.getName(), it) }


//


//----------------------------------------------------------------------------//
// mito_preprocessing pipeline
//----------------------------------------------------------------------------//

//

workflow TENX {
    csvChannel = Channel
        .fromPath(params.sc_tenx_csv)
        .splitCsv(header: true, sep: ',')
    csvChannel
        .map { row -> tuple(row.path_source, row.name_new_path_bulk, row.id_we_want) }
        .set { csvTuples }

    CREATE_FOLDER(csvTuples)  
    tenx(CREATE_FOLDER.out.samples)

}

//

workflow TENX_MITO {

    tenx(ch_tenx)
    maester(ch_maester, tenx.out.filtered, tenx.out.bam)

} 

//

workflow BULK_GBC {
 
    bulk_gbc(ch_bulk_gbc)

}

//

workflow TENX_GBC {

    tenx(ch_tenx)
    sc_gbc(ch_sc_gbc, tenx.out.filtered)

}

//

workflow TENX_GBC_MITO {

    tenx(ch_tenx)
    sc_gbc(ch_sc_gbc, tenx.out.filtered)
    maester(ch_maester, tenx.out.filtered, tenx.out.bam)

}

//

// Mock
workflow {
    
    Channel.of(1,2,3,4) | view

}