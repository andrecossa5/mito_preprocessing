#!/usr/bin/python

"""
Cell assignment script.
"""


##


# Libraries
import os
import sys
import argparse

# Create the parser
my_parser = argparse.ArgumentParser(
    prog='cell_assignment',
    description=
    """
    Script for clone calling and cell assignment.
    """
)

# Input
my_parser.add_argument(
    '--sample',
    type=str,
    default=None,
    help='Sample name. Default: None.'
)

# Input sc GBC reads
my_parser.add_argument(
    '--path_sc',
    type=str,
    default=None,
    help='Path to input sc GBC reads elements. Default: None.'
)

# UMI threshold
my_parser.add_argument(
    '--umi_treshold',
    type=int,
    default=5,
    help='Min number of UMIs to consider a CBC-GBC combination supported. Default: 5.'
)

# p_treshold
my_parser.add_argument(
    '--p_treshold',
    type=float,
    default=.5,
    help='Max p_poisson treshold to consider a CBC-GBC combination supported. Default: .001.'
)

# ratio_to_most_abundant_treshold
my_parser.add_argument(
    '--max_ratio_treshold',
    type=float,
    default=.8,
    help='Min ratio between a GBC nUMIs and the most abundant (nUMIs) GBC found for a given CBC. Default: .8.'
)

# Normalized abundance
my_parser.add_argument(
    '--normalized_abundance_treshold',
    type=float,
    default=.8,
    help='Min abundance (nUMIs fraction within a cell) of a CBC-GBC combination. Default: .8.'
)


##


# Parse arguments
args = my_parser.parse_args()
sample = args.sample
path_sc = args.path_sc
umi_treshold = args.umi_treshold
p_treshold = args.p_treshold
max_ratio_treshold = args.max_ratio_treshold
normalized_abundance_treshold = args.normalized_abundance_treshold


# Import code
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from helpers import *
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))
from utils import encode_image_b64, resolve_working_dir_and_user  # or any other functions you need


##


def main():

    try:

        """
        Custom workflow.
        Brings together filtering and correction strategies from difference works:
        * Adamson et al., Dixit et al., Cell 2016
        * Weinreb et al., Science 2020
        * Roda and Cossa et al., Cancer Research 2023
        * Nadalin et al., pre-print on biorxiv 2023
        """

        cell_assignment_workflow(
            path_sc,
            sample=sample,
            umi_treshold=umi_treshold,
            p_treshold=p_treshold,
            max_ratio_treshold=max_ratio_treshold,
            normalized_abundance_treshold=normalized_abundance_treshold
        )

    except:

        raise Exception(
            f'''
            Some problem has been encoutered with the custom_workflow for the {sample} sample...
            '''
        )


    ##


# Run
if __name__ == '__main__':
    main()
