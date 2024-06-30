// mi_to_preprocessing, working
nextflow.enable.dsl = 2

// Include here
include { bulk_gbc } from "./subworkflows/bulk_gbc/main"
include { tenx } from "./subworkflows/tenx/main"
include { sc_gbc } from "./subworkflows/sc_gbc/main"
include { maester } from "./subworkflows/maester/main"

// Create folders
process CREATE_FOLDER_TENX {

    input:
        tuple val(path_source), val(name_new_path_bulk), val(id_we_want)

    output:
        tuple val(name_new_path_bulk), path(name_new_path_bulk), emit: samples

    script:
    """ 
    mkdir -p ${name_new_path_bulk}
    cd ${name_new_path_bulk}
    ln -s ${path_source}/${name_new_path_bulk}/*R2*.fastq.gz .
    ln -s ${path_source}/${name_new_path_bulk}/*R1*.fastq.gz .
    """

    stub:
    """
    mkdir -p ${name_new_path_bulk}
    """
}

process CREATE_FOLDER_MAESTER {

    input:
        tuple val(path_source), val(name_new_path_bulk), val(id_we_want)

    output:
        tuple val(name_new_path_bulk), path(name_new_path_bulk), emit: samples

    script:
    """ 
    mkdir -p ${name_new_path_bulk}
    cd ${name_new_path_bulk}
    ln -s ${path_source}/${name_new_path_bulk}/*R2*.fastq.gz .
    ln -s ${path_source}/${name_new_path_bulk}/*R1*.fastq.gz .
    """

    stub:
    """
    mkdir -p ${name_new_path_bulk}
    """
}

process CREATE_FOLDER_GBC {

    input:
        tuple val(path_source), val(name_new_path_bulk), val(id_we_want)

    output:
        tuple val(name_new_path_bulk), path(name_new_path_bulk), emit: samples

    script:
    """ 
    mkdir -p ${name_new_path_bulk}
    cd ${name_new_path_bulk}
    ln -s ${path_source}/${name_new_path_bulk}/*R2*.fastq.gz .
    ln -s ${path_source}/${name_new_path_bulk}/*R1*.fastq.gz .
    """

    stub:
    """
    mkdir -p ${name_new_path_bulk}
    """
}


//----------------------------------------------------------------------------//
// mito_preprocessing pipeline
//----------------------------------------------------------------------------//

workflow TENX {
    csvChannel_tenx = Channel
        .fromPath(params.sc_tenx_csv)
        .splitCsv(header: true, sep: ',')
        .map { row -> tuple(row.Path_source, row.Name_new_path_sc, row.ID_we_want) }

    CREATE_FOLDER_TENX(csvChannel_tenx).set { create_folder_tenx_out }
    tenx(create_folder_tenx_out.samples)
}

//

workflow TENX_MITO {
    csvChannel_tenx = Channel
        .fromPath(params.sc_tenx_csv)
        .splitCsv(header: true, sep: ',')
        .map { row -> tuple(row.Path_source, row.Name_new_path_sc, row.ID_we_want) }

    CREATE_FOLDER_TENX(csvChannel_tenx).set { create_folder_tenx_out }
    tenx(create_folder_tenx_out.samples)

    csvChannel_maester = Channel
        .fromPath(params.sc_maester_csv)
        .splitCsv(header: true, sep: ',')
        .map { row -> tuple(row.Path_source, row.Name_new_path_sc, row.ID_we_want) }

    CREATE_FOLDER_MAESTER(csvChannel_maester).set { create_folder_maester_out }
    maester(create_folder_maester_out.samples, tenx.out.filtered, tenx.out.bam)
} 

//

workflow BULK_GBC {
    bulk_gbc(ch_bulk_gbc)
}

//

workflow TENX_GBC {    
    csvChannel_tenx = Channel
        .fromPath(params.sc_tenx_csv)
        .splitCsv(header: true, sep: ',')
        .map { row -> tuple(row.Path_source, row.Name_new_path_sc, row.ID_we_want) }

    CREATE_FOLDER_TENX(csvChannel_tenx).set { create_folder_tenx_out }
    tenx(create_folder_tenx_out.samples)

    csvChannel_gbc = Channel
        .fromPath(params.sc_gbc_csv)
        .splitCsv(header: true, sep: ',')
        .map { row -> tuple(row.Path_source, row.Name_new_path_sc, row.ID_we_want) }

    CREATE_FOLDER_GBC(csvChannel_gbc).set { create_folder_gbc_out }
    sc_gbc(create_folder_gbc_out.samples, tenx.out.filtered)
}

//

workflow TENX_GBC_MITO {
    csvChannel_tenx = Channel
        .fromPath(params.sc_tenx_csv)
        .splitCsv(header: true, sep: ',')
        .map { row -> tuple(row.Path_source, row.Name_new_path_sc, row.ID_we_want) }

    CREATE_FOLDER_TENX(csvChannel_tenx).set { create_folder_tenx_out }
    tenx(create_folder_tenx_out.samples)

    csvChannel_gbc = Channel
        .fromPath(params.sc_gbc_csv)
        .splitCsv(header: true, sep: ',')
        .map { row -> tuple(row.Path_source, row.Name_new_path_sc, row.ID_we_want) }

    CREATE_FOLDER_GBC(csvChannel_gbc).set { create_folder_gbc_out }
    sc_gbc(create_folder_gbc_out.samples, tenx.out.filtered)

    csvChannel_maester = Channel
        .fromPath(params.sc_maester_csv)
        .splitCsv(header: true, sep: ',')
        .map { row -> tuple(row.Path_source, row.Name_new_path_sc, row.ID_we_want) }

    CREATE_FOLDER_MAESTER(csvChannel_maester).set { create_folder_maester_out }
    maester(create_folder_maester_out.samples, tenx.out.filtered, tenx.out.bam)
}

//

// Mock workflow
workflow {
    Channel.of(1,2,3,4) | view
}
