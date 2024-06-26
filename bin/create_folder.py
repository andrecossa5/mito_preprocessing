#!/usr/bin/python

import os
import sys
import pandas as pd
import numpy as np

# Read sample metadata files
path_meta = sys.argv[1]
path_new_folder = sys.argv[2]
overwrite = sys.argv[3]

##


# Helper function
def create_folders(path_mother, new_folder_name, df, overwrite=False):
    """
    Create samples folder.
    """

    os.chdir(path_mother)

    if overwrite:
        os.system(f'rm {new_folder_name}')
    
    os.mkdir(new_folder_name)
    os.chdir(path_mother)

    # Here we go
    for i in range(df.shape[0]):

        os.chdir(os.path.join(path_mother, new_folder_name))
        l = df.iloc[i,:].to_list()
        path_source = os.path.join(l[0], l[1])

        if os.path.exists(path_source):

            if not os.path.exists(os.path.join(path_mother, new_folder_name, l[2])):
                print(f'Creating {l[2]}: {path_source} exists')
                os.mkdir(l[2])
                os.chdir(l[2])
                os.system(f'ln -s {path_source}/*_R1_*.fastq.gz .')
                os.system(f'ln -s {path_source}/*_R2_*.fastq.gz .')

            elif os.path.exists(os.path.join(path_mother, new_folder_name, l[2])):
                print(f'Adding file links to {l[2]}: {path_source} exists')
                os.chdir(l[2])
                os.system(f'ln -s {path_source}/*_R1_*.fastq.gz .')
                os.system(f'ln -s {path_source}/*_R2_*.fastq.gz .')

        else:
            print(f'Cannot create {l[2]}: {path_source} does NOT exist...')


##


# Checks
if path_new_folder.endswith('/'):
    path_new_folder = path_new_folder[:-1]

path_mother = '/'.join(path_new_folder.split('/')[:-1])
new_folder_name = path_new_folder.split('/')[-1]
assert os.path.exists(path_mother)

df = pd.read_csv(path_meta)
for i in range(df.columns.size):
    df.iloc[:,i] = df.iloc[:,i].apply(lambda x: str(x).replace(u'\xa0', u''))

overwrite = True if overwrite == 'yes' else False
    
# Here we go
if not os.path.exists(path_new_folder):
    print(f'Creating new folder {new_folder_name} at {path_mother}...')
    create_folders(path_mother, new_folder_name, df)

elif os.path.exists(path_new_folder) and not overwrite:
    raise ValueError('Folder already present... Aborting.')

elif os.path.exists(path_new_folder) and overwrite:
    print('Folder already present, but the overwrite option is on. Overwriting!')
    create_folders(path_mother, new_folder_name, df, overwrite=True)
else:
    raise ValueError('Check inputs man...')


##