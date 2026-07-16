<div align="center">

# nf-lenti

*Lentiviral-barcode-based single-cell lineage tracing (Nextflow)*

[![Nextflow](https://img.shields.io/badge/nextflow-%E2%89%A520.01.0-brightgreen.svg)](https://www.nextflow.io/)
[![Docker](https://img.shields.io/badge/docker-enabled-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://img.shields.io/badge/DOI-10.1101%2F2025.06.17.660165-blue)](https://doi.org/10.1101/2025.06.17.660165)

</div>

## Overview

nf-lenti is a Nextflow pipeline for lentiviral-barcode-based single-cell lineage tracing (GBC-scLT).
Cells are labelled with expressed, random genetic barcodes (GBCs) integrated by a lentiviral cassette;
nf-lenti processes the resulting sequencing data to build a GBC reference, call clones and assign single
cells to their clonal labels. Two entrypoints are provided:

1. `BULK_GBC` — build a **bulk** GBC reference from bulk DNA GBC libraries (search, correct and count GBCs).
2. `TENX_GBC` — call clones from **single-cell** (10x) GBC libraries (consensus GBC reads, CBC-GBC combination
   filtering and cell assignment).

### Key Features

- 📁 **Multiple raw data input formats**: separate TENX/GBC FASTQ libraries, GBC-only FASTQs, pre-aligned BAMs, or a single set of mixed (TENX + GBC) FASTQs.
- 🧬 **Flexible lentiviral barcode definition**: configurable cassette contig, anchor sequence, GBC start and length.
- 🎯 **1-mismatch GBC matching**: sensitive anchor matching shared between bulk and single-cell splitting.
- ⚡ **Consensus GBC reads**: UMI-based consensus calling with [fgbio](https://fulcrumgenomics.github.io/fgbio/).
- ☁️ **Scalable execution**: local, HPC, and cloud environment support.

## Quick Start

### Prerequisites

- [Nextflow](https://www.nextflow.io/) (≥20.01.0)
- [Docker](https://www.docker.com/), [Singularity/Apptainer](https://apptainer.org/) (preferred), or [Conda](https://conda.io/)

### Basic Usage

nf-lenti runs on any machine/HPC cluster supporting Docker/Singularity containers:

```bash
nextflow run main.nf -c <user.config> -params-file <params.json> -profile <chosen_profiles> -entry <chosen_entrypoint>
```

With a single command, the user can specify custom:

- Run configs: `-c <user.config>`
- Parameters: `-params-file <params.json>`
- Profiles: `-profile <chosen_profiles>` (e.g. `docker`, `singularity`, `conda`, `local`)

and choose one of the two entrypoints with `-entry <chosen_entrypoint>` (`BULK_GBC` or `TENX_GBC`).
See [configuration](https://www.nextflow.io/docs/latest/config.html) for details.

### Input sample sheets

The `--input_sheet` parameter always points to a CSV sample sheet. Its columns depend on the entrypoint and,
for `TENX_GBC`, on `--input_type`.

**`BULK_GBC`** — one row per bulk sample:

| ID_we_want | path_bulk | folder_name_bulk |
|------------|-----------|------------------|
| `sample_name` | `parent path` | `FASTQs folder name` |

**`TENX_GBC`**, `--input_type` = `fastq` — separate TENX and GBC libraries (two rows per sample):

| sample | fastq_folder | library |
|--------|--------------|---------|
| `sample_name` | `FASTQs folder path` | `TENX` |
| `sample_name` | `FASTQs folder path` | `GBC` |

**`TENX_GBC`**, `--input_type` = `fastq,GBC` — GBC library plus external cell barcodes:

| sample | fastq_folder | cell_barcodes |
|--------|--------------|---------------|
| `sample_name` | `GBC FASTQs folder path` | `cell_barcodes.txt path` |

**`TENX_GBC`**, `--input_type` = `bam` — pre-aligned GBC library plus external cell barcodes:

| sample | bam | cell_barcodes |
|--------|-----|---------------|
| `sample_name` | `GBC bam path` | `cell_barcodes.txt path` |

**`TENX_GBC`**, `--input_type` = `fastq,mixed` — a single set of FASTQs with TENX and GBC reads mixed
together (reads are split by the R2 lentiviral anchor, then processed as in `fastq`):

| sample | fastq_folder |
|--------|--------------|
| `sample_name` | `mixed FASTQs folder path` |

The `--outdir` parameter is always required.

## Parameters

nf-lenti parameters are grouped into distinct groups controlling one or both entrypoints. See
`nextflow.config` and `nextflow_schema.json` for the full type information and defaults.

### Input/Output parameters

| Parameter | Description | Default | Type |
|-----------|-------------|---------|------|
| `--input_type` | Input data type for `TENX_GBC` [`fastq`, `fastq,GBC`, `bam`, `fastq,mixed`] | `fastq` | String |
| `--input_sheet` | Input sample sheet (CSV) | `–` | Path |
| `--outdir` | Output directory path | `–` | Path |

### Alignment parameters

| Parameter | Description | Default | Type |
|-----------|-------------|---------|------|
| `--ref` | STARsolo reference directory (with the lentiviral cassette contig) | `–` | Path |
| `--tenx_whitelist` | 10x cell barcode whitelist URL or path | [10x v3 whitelist](https://teichlab.github.io/scg_lib_structs/data/10X-Genomics/3M-february-2018.txt.gz) | Path/URL |

### Lentiviral barcode parameters

| Parameter | Description | Default | Type |
|-----------|-------------|---------|------|
| `--lenti_string` | Name of the lentiviral cassette contig | `lentiCassette` | String |
| `--lenti_pattern` | Lentiviral anchor sequence preceding the GBC | `–` | String |
| `--lenti_start` | 0-based offset of the GBC within the read (leading bases to skip) | `33` | Integer |
| `--lenti_bc_length` | GBC length (bp) | `18` | Integer |

`--lenti_start` is 0-based: it is used directly by the single-cell Python extractor and converted to
1-based inside the bulk `awk` extractor, so the same value extracts the same region in both.

### Sequencing data preprocessing parameters

| Parameter | Description | Default | Type |
|-----------|-------------|---------|------|
| `--CBs_chunk_size` | Cell barcodes chunk size for parallel processing | `3000` | Integer |
| `--fgbio_UMI_consensus_mode` | UMI-based read grouping strategy | `Identity` | String |
| `--fgbio_UMI_consensus_edits` | Max UMI edit distance for read grouping | `0` | Integer |
| `--fgbio_min_reads` | Min reads for consensus sequence generation | `10` | Integer |
| `--fgbio_base_error_rate` | Max fraction of discordant bases in a read group | `0.2` | Float |
| `--fgbio_min_base_quality` | Min base-calling quality of consensus bases | `30` | Integer |
| `--fgbio_min_alignment_quality` | Min mapping quality of grouped reads | `60` | Integer |

### Clone calling parameters

| Parameter | Description | Default | Type |
|-----------|-------------|---------|------|
| `--umi_treshold` | Min nUMIs to consider a CBC-GBC combination supported | `5` | Integer |
| `--p_treshold` | Max Poisson p-value to consider a CBC-GBC combination supported | `1` | Float |
| `--max_ratio_treshold` | Min ratio of a GBC nUMIs to the most abundant GBC in a CBC | `0.5` | Float |
| `--normalized_abundance_treshold` | Min within-cell nUMIs fraction of a CBC-GBC combination | `0.5` | Float |

### Bulk GBC parameters

| Parameter | Description | Default | Type |
|-----------|-------------|---------|------|
| `--bulk_gbc_spikeins_table` | Spike-ins table to remove from bulk GBC counts (optional) | `null` | Path |
| `--bulk_gbc_graph_clustering_hamming_treshold` | Max Hamming distance for GBC clustering | `3` | Integer |
| `--bulk_gbc_min_n_reads` | Min reads for a corrected GBC to be retained | `10` | Integer |

## Configuration

Any custom configuration can be passed to nf-lenti with the `-c <user.config>` option. See the
[`config/user.config`](config/user.config) file for a minimal example for an HPC environment.

## Citation

If you use nf-lenti in your research, please cite:

*MiTo: tracing the phenotypic evolution of somatic cell lineages via mitochondrial single-cell multi-omics. Andrea Cossa, Alberto Dalmasso, Guido Campani, Elisa Bugani, Chiara Caprioli, Noemi Bulla, Andrea Tirelli, Yinxiu Zhan, Pier Giuseppe Pelicci. biorxiv. doi:https://doi.org/10.1101/2025.06.17.660165*

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
