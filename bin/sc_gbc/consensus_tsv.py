#!/usr/bin/python

"""
Sript to split create a .tsv of read_id, cbc, umi, and feature 
(aka, GBC 18bp random integrated barcodes) read elements. 
"""


import sys
import pysam


##


# Args
path_bam = sys.argv[1]
cell = sys.argv[2]


##


def main():
    with pysam.AlignmentFile(path_bam, 'rb', check_sq=False) as bam:
        with open(f'{cell}_consensus_filtered.tsv', 'w') as tsv:
            tsv.write("read_ID\tCBC\tUMI\tGBC\tn_consensus_read\n")
            for i, alignment in enumerate(bam): 
                feature = alignment.seq[33:33+18]
                umi = alignment.get_tag("MI")
                n_consensus_read = alignment.get_tag("cD")
                tsv.write(f"read_{i}\t{cell}\t{umi}\t{feature}\t{n_consensus_read}\n")

# Run 
if __name__ == '__main__':
    main()


