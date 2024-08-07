"""
Correlation site-coverage and gene expression SCM-seq
"""

import os
import numpy as np
import pandas as pd
from mito_utils.plotting_base import *
matplotlib.use('macOSX')


##


# Explore
sample = 'sAML1'
path_results = f'/Users/IEO5505/Desktop/example_mito/results/test_nanopore_{sample}'
path_counts = os.path.join(path_results, 'counts_table.csv') 
path_expr = os.path.join(f'/Users/IEO5505/Desktop/example_mito/scratch/nuclear_SNVs_expression_10x.csv')

allele_counts = pd.read_csv(path_counts)
expression = pd.read_csv(path_expr, index_col=0)
expression.index = expression.index.map(lambda x: x.split('-')[0])

df = allele_counts.query('MUT>0 or WT>0')
MUT = df.pivot(index='cell', columns='gene', values='MUT').fillna(0)
WT = df.pivot(index='cell', columns='gene', values='WT').fillna(0)
coverage = MUT+WT

cells = list(set(coverage.index) & set(expression.index))
df_ = coverage.loc[cells].mean(axis=0).to_frame('coverage_SCM').join(expression.loc[cells].mean(axis=0).to_frame('expression_10x'))

##

# All cells, aggregated with means
fig, ax = plt.subplots(figsize=(5,5))
sns.regplot(data=df_, x='expression_10x', y='coverage_SCM', scatter=False)
ax.plot(df_['expression_10x'], df_['coverage_SCM'], 'ko', markersize=10)
format_ax(ax=ax, title=f'Corr: {df_.corr().iloc[1,0]:.2f}', xlabel='n UMIs (expression, 10x)', ylabel='n UMIs (per target base, SCM-seq)')
fig.tight_layout()
fig.savefig(os.path.join(path_results, 'corr_SCM_10x_all_cells.png'), dpi=1000)

##

# All calls
df_ = (
    df.assign(nUMIs_SCM=lambda x: x['MUT']+x['WT']+x['MIS']).drop(columns=['MUT', 'WT', 'MIS'])
    .merge( 
        expression.reset_index().rename(columns={'index':'cell'})
        .melt(id_vars='cell', value_name='nUMIs_10x', var_name='gene'),
        on=['cell', 'gene']
    )
)

fig, ax = plt.subplots(figsize=(5,5))
sns.regplot(data=df_, x='nUMIs_10x', y='nUMIs_SCM', scatter=False)
ax.plot(df_['nUMIs_10x'], df_['nUMIs_SCM'], 'ko', markersize=2)
format_ax(ax=ax, title=f'Corr: {df_[["nUMIs_SCM", "nUMIs_10x"]].corr().iloc[1,0]:.2f}', 
          xlabel='n UMIs (expression, 10x)', ylabel='n UMIs (per target base, SCM-seq)')
fig.tight_layout()
fig.savefig(os.path.join(path_results, 'corr_SCM_10x_all_cells.png'), dpi=1000)


##



