"""
Script to get all the useful plots from Count matrix before and after decontamination
"""

##


import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from plotting_utils._plotting_base import *
import umap
from mito_utils.kNN import *
from mito_utils.clustering import *
from scipy.spatial.distance import pdist, squareform
from itertools import combinations

sys.path.append("/Users/ieo6943/Documents/Guido/mito_preprocessing/bin/RNA_decontamination")
sys.path.append("/Users/ieo6943/Documents/Guido/mito_preprocessing/bin/sc_gbc")
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from decontamination_utils import *
from helpers import *

    
##


# Paths
path_main = '/Users/ieo6943/Documents/data/8_clones'
##path_main = '/Users/ieo6943/Documents/data/complex_experiment'
path_decontX = os.path.join(path_main,'count_matrix_&_DecontX')
path_count = os.path.join(path_main, 'counts.pickle')
#path_results = '/Users/ieo6943/Documents/results/complex_experiment/'
path_results = '/Users/ieo6943/Documents/results/8_clones/'

##


# Parameters
correction_type='reference' 
umi_treshold=5
p_treshold=1
max_ratio_treshold=.5
normalized_abundance_treshold=.5
th_list = list(range(0, 101, 20))


##


#Choose the plots you desire
moi_histogram = False
true_contamination_vs_decontXcontamination_correlation = False
UMI_GBC_DecontX_correction_percentage_histogram = False
GBC_completely_removed_relevance_boxplot = False
median_GBC_abundance_boxplot = False
density_plot = False
GBCs_cluster_violin_distribution = False
DecontX_efficiency_of_decontamination_box_plot = False
loss_good_read_boxplot = False
decontaminated_filtered = False
distribution_read_UMI = True
UMI_error_distance = True 

##


with open(path_count, 'rb') as p:
    COUNTS= pickle.load(p)

super_data = {'corrections_perc':[], 'complete_correction':[], 'median_data':{}, 'loss_good_read':[], 'loss_good_UMI':[], 'change_in_GBC': []}
decontamination_efficency_data = {'C/GBC':[], 'C_dec/GBC_dec':[], 'GBC_dec/GBC':[], 'C_dec/C':[], 'C_dec':[], 'C':[] }
decontamination_filtering = {'change_in_GBC':[], 'survived_cell':[]}

##


#Calculating the mean hamming distance of the UMI sequences for eac group of CBC-GBC ---- OPTION 1

counts = mark_UMIs(COUNTS[correction_type], coverage_treshold=0)
unique_UMI_df = counts.groupby(['CBC', 'GBC_reference'])['UMI'].unique().to_frame('umi').reset_index()
unique_UMI_df['humming_mean'] = 0
unique_UMI_df['humming_error'] = 0

from sklearn.metrics.pairwise import pairwise_distances
import numpy as np

hist_bad_UMI_perc = []
hist_bad_UMI = []
strange = []
for k in range(unique_UMI_df['umi'].shape[0]):
    print(k, ' su ', unique_UMI_df['umi'].shape[0])
    stringhe = unique_UMI_df['umi'][k]
    str_to_int = np.array([[ord(char) for char in s] for s in stringhe])
    distance = 12*pairwise_distances(str_to_int, metric='hamming')
    bad_UMI_perc = ((distance<3).sum(axis=1)-1)/len(stringhe)
    bad_UMI = (distance<3).sum(axis=1)-1
    if bad_UMI.std()==0:
        strange.append(k)
    hist_bad_UMI_perc.append([bad_UMI_perc.mean(), bad_UMI_perc.std()])
    hist_bad_UMI.append([bad_UMI.mean(), bad_UMI.std()])


#perc
hist_bad_UMI_perc = np.array(hist_bad_UMI_perc)
pseudo_zero = (hist_bad_UMI_perc[:,1][hist_bad_UMI_perc[:,1]!=0].min())/10
weights = 1/(hist_bad_UMI_perc[:,1]+pseudo_zero )**2
bad_UMI_null_std_mean_perc = hist_bad_UMI_perc[:,0][hist_bad_UMI_perc[:,1]==0].mean()
bad_UMI_mean_perc = np.average(hist_bad_UMI_perc[:,0], weights=weights)

fig = plt.figure()
sns.histplot(hist_bad_UMI_perc[:,0])
#sns.histplot(hist_bad_UMI[:,0][hist_bad_UMI[:,1]==0])
plt.xlabel(f'mean % of UMI with hamming distance <3')
#plt.ylabel(y_label)
plt.title(f'mean % of UMI with hamming distance <3 for each CBC-GBC')
fig.savefig(os.path.join(path_results, 'bad_UMI_perc.png'), dpi=300)

#abs
hist_bad_UMI = np.array(hist_bad_UMI)
pseudo_zero = (hist_bad_UMI[:,1][hist_bad_UMI[:,1]!=0].min())/10
weights = 1/(hist_bad_UMI[:,1]+pseudo_zero )**2
bad_UMI_null_std_mean = hist_bad_UMI[:,0][hist_bad_UMI[:,1]==0].mean()
bad_UMI_mean = np.average(hist_bad_UMI[:,0], weights=weights)
hist_bad_UMI[:,0].sum()

fig = plt.figure()
sns.histplot(hist_bad_UMI[:,0])
#sns.histplot(hist_bad_UMI[:,0][hist_bad_UMI[:,1]==0])
plt.xlabel(f'mean # of UMI with hamming distance <3')
#plt.ylabel(y_label)
plt.title(f'mean # of UMI with hamming distance <3 for each CBC-GBC')
fig.savefig(os.path.join(path_results, 'bad_UMI.png'), dpi=300)
##


## Create all the neede distributions
for coverage_treshold in th_list:
    print('coverage_treshold =', coverage_treshold )
     
    #Creation of the all the dataframe
    m_df = pd.read_csv(os.path.join(path_decontX, f'M_{coverage_treshold}.csv'), index_col=0) #count matrix
    m_df_dec = pd.read_csv(os.path.join(path_decontX, f'M_{coverage_treshold}_dec.csv'), index_col=0) #decontaminated count matrix
    z = pd.read_csv(os.path.join(path_decontX, f'z{coverage_treshold}.csv')) #cluster label of DecontX
    contamination = list(pd.read_csv(os.path.join(path_decontX, f'contamination_{coverage_treshold}.csv')).values.flatten()) # DecontX contamination level for each cell
    
    #Counts tables from pickle
    counts = mark_UMIs(COUNTS[correction_type], coverage_treshold=coverage_treshold)
    df_combos = get_combos(counts, gbc_col=f'GBC_{correction_type}')
    df_combos_dec = get_df_combos(m_df_dec)

    m_df_l = pd.DataFrame(m_df.idxmax(axis=1), columns=['GBC_reference'])
    m_df_dec_l = pd.DataFrame(m_df_dec.idxmax(axis=1), columns=['GBC_reference'])
    m_df_dec_l.index.name = 'CBC'

    if decontaminated_filtered==True:
    #Filtered Count matrix
        M, _ = filter_and_pivot(
        df_combos, 
        umi_treshold=umi_treshold, 
        p_treshold=p_treshold, 
        max_ratio_treshold=max_ratio_treshold,
        normalized_abundance_treshold=normalized_abundance_treshold
        )  

        #Filtered and decontaminated Count matrix
        M_dec, _ = filter_and_pivot(
        df_combos_dec, 
        umi_treshold=umi_treshold, 
        p_treshold=p_treshold, 
        max_ratio_treshold=max_ratio_treshold,
        normalized_abundance_treshold=normalized_abundance_treshold
        )  
        
        M_l = pd.DataFrame(M.idxmax(axis=1), columns=['GBC_reference'])
        M_dec_l = pd.DataFrame(M_dec.idxmax(axis=1), columns=['GBC_reference'])
        M_merge = pd.merge(M_l, M_dec_l, on=['CBC', 'GBC_reference'], how='inner' )
        decontamination_filtering['change_in_GBC'].append((M.shape[0]- M_merge.shape[0])/M.shape[0])
        decontamination_filtering['survived_cell'].append((M_dec.shape[0]- M_merge.shape[0])/M.shape[0])

    ##


    # GBC abundance for eac cell
    if median_GBC_abundance_boxplot==True:
        print ('median_GBC_abundance_boxplot')

        super_data['median_data'][coverage_treshold]=df_combos.groupby('CBC')['normalized_abundance'].median().values

    # histogram of the MOI of each cell
    if moi_histogram==True:
        print('moi_histogram')

        moi_df=list(m_df.count(axis=1))
        moi_df_dec=list(m_df_dec.count(axis=1))
        fig = double_hist(measure_before=moi_df, measure_after=moi_df_dec, title='multiplicity of infection for each cell', value='moi')
        fig.savefig(os.path.join(path_results, f'Multiple of infection_{coverage_treshold}.png'), dpi=300)

    # correlational scatter plot of true contamination and contamination detected by DecontX
    if true_contamination_vs_decontXcontamination_correlation==True:
        print('moi_histogram')

        major_feature_density = m_df.max(axis=1)/m_df.sum(axis=1)
        other_feature_density=list(1-np.array(major_feature_density))
        fig = scatter_correlation(other_feature_density, contamination, coverage_treshold)
        fig.savefig(os.path.join(path_results, f'correlation_contamination_{coverage_treshold}.png'), dpi=300)

    # percentage of the variation in the UMi counts and GBC counts after decontamination
    if UMI_GBC_DecontX_correction_percentage_histogram==True:
        print('UMI_GBC_DecontX_correction_percentage_histogram')

        delta_UMI_GBC=UMI_GBC_variation(m_df, m_df_dec)
        super_data['corrections_perc'].append(delta_UMI_GBC)

    # it returns for each cell the list of the normalized abundancy of the umi counts associated to each GBC tha have been removed by DecontX
    if GBC_completely_removed_relevance_boxplot ==True:
        print('GBC_completely_removed_relevance_boxplot')

        total_n_correction, complete_correction_relevance=complete_corr_relevance(m_df, m_df_dec)
        percentage_complete_correction=complete_correction_relevance.shape[0]/total_n_correction
        super_data['complete_correction'].append([percentage_complete_correction, complete_correction_relevance])

    #KDE plot: GBC normalized abundance vs GBC max ratio
    if density_plot==True:
        print('density_plot')

        fig, axs = plt.subplots(1, 2, figsize=(12, 6))
        sns.kdeplot(data=df_combos_dec, x = df_combos_dec['max_ratio'], y =df_combos_dec['normalized_abundance'], ax=axs[1])
        axs[1].set_title('After decontamination')
        sns.kdeplot(data=df_combos, x = df_combos['max_ratio'], y =df_combos['normalized_abundance'], ax=axs[0])
        axs[0].set_title('Before decontamination')
        fig.suptitle(f'Density plot{coverage_treshold}', fontsize=16)
        fig.savefig(os.path.join(path_results, f'Density_{coverage_treshold}.png'), dpi=300)
    
    #Violin distribution of the GBCs in each DecontX cluster
    if GBCs_cluster_violin_distribution==True:
        print('GBCs_cluster_violin_distribution')

        df = pd.DataFrame({'CBC': list(m_df.index), 'cluster': list(z.values.flatten())})
        z_cluster = np.unique(z)
        combos = {'not_decontaminated': df_combos, 'decontaminated':df_combos_dec}
        dataset = {'not_decontaminated':[], 'decontaminated':[]}
        for key in combos.keys():

            df_combos_th= pd.merge(combos[key], df, on = 'CBC', how = 'inner')
            my_dict = dict(zip(m_df.columns, range(1,m_df.shape[1]+1)))
            df_combos_th['GBC'] = df_combos_th['GBC'].replace(my_dict)
            cluster={}
            cluster_data= {}
            palette = sns.color_palette("husl" ,len(z_cluster))
            plt.figure()

            for c in z_cluster:

                cluster[c]=df_combos_th[['normalized_abundance','GBC','CBC']][df_combos_th['cluster']== c]
                cluster[c]['normalized_abundance'] = round(cluster[c]['normalized_abundance']/len(np.unique(cluster[c]['CBC']))*1000)
                cluster_data[c] = cluster[c].groupby('GBC')['normalized_abundance'].sum().reset_index()
                data=[]

                for gbc in list(cluster_data[c]['GBC']):
                    data += [gbc] * int(cluster_data[c][cluster_data[c]['GBC']==gbc]['normalized_abundance'].values)

                dataset[key].append(data)

            fig = plt.figure(figsize=(6,4))
            positions = z_cluster
            sns.violinplot(data=dataset[key], positions=positions)
            plt.xlabel('clusters')
            plt.ylabel('Normalized abundance of GBC')
            plt.title(f'Coverage threshold ={coverage_treshold} {key}')
            fig.savefig(os.path.join(path_results, f'Violin_{coverage_treshold}_{key}.png'), dpi=300)

    #Efficency of the decontamination
    if DecontX_efficiency_of_decontamination_box_plot==True:

        GBC_major = m_df.max(axis=1)/m_df.sum(axis=1)
        Contamination_count = m_df.sum(axis=1) - m_df.max(axis=1)
        trueContamination = 1 - GBC_major
        decontamination_efficency_data['C/GBC'].append(list(trueContamination/GBC_major))
        decontamination_efficency_data['C'].append(list(Contamination_count))

        
        GBC_major_dec = m_df_dec.max(axis=1)/m_df_dec.sum(axis=1)
        Contamination_count_dec = m_df_dec.sum(axis=1) - m_df_dec.max(axis=1)
        trueContamination_dec = 1- GBC_major_dec
        

        decontamination_efficency_data['C_dec/GBC_dec'].append(list(trueContamination_dec/GBC_major_dec))
        decontamination_efficency_data['C_dec'].append(list(Contamination_count_dec))

        decontamination_efficency_data['C_dec/C'].append(list(trueContamination_dec/trueContamination))
        decontamination_efficency_data['GBC_dec/GBC'].append(list(GBC_major_dec/GBC_major))

    if loss_good_read_boxplot==True:

        loss_good_GBC = len(m_df_l[m_df_l['GBC_reference'] != m_df_dec_l['GBC_reference']])/len(m_df_l)*100
        diff = m_df - m_df_dec
        loss_good_UMI_perc = []
        for i in range(diff.shape[0]):
            loss_good_UMI_perc.append(diff.iloc[i][m_df.iloc[i].idxmax()]/m_df.iloc[i].max())
        m_df_l['loss_good_UMI'] = loss_good_UMI_perc
        m_df_l['CBC'] = m_df.index
        m_df_l.index.name = ''
        merged_df = pd.merge(counts, m_df_l, on=['CBC', 'GBC_reference'], how='left')
        merged_df.fillna(0, inplace=True)
        merged_df['loss_good_read']=merged_df['loss_good_UMI']*counts['count']
        loss_good_read = merged_df.groupby(['CBC', 'GBC_reference'])[['loss_good_read', 'count']].sum().reset_index()
        super_data['loss_good_read'].append(loss_good_read[loss_good_read['loss_good_read']!=0]['loss_good_read'].values)
        super_data['loss_good_UMI'].append(loss_good_UMI_perc)
        super_data['change_in_GBC'].append(loss_good_GBC)
    
    if distribution_read_UMI==True:
        filtered = counts.loc[lambda x: x['status']=='Retain']
        R_median = filtered.groupby(['CBC', 'GBC_reference'])['count'].median().reset_index()
        R_median = R_median.rename(columns={'count': 'read_median'})
        filtered= pd.merge(filtered, R_median, on=['CBC', 'GBC_reference'], how='left') 
        R = filtered.pivot_table(index='CBC', columns='GBC_reference', values='read_median')
        R[R.isna()] = 0
        decontamination_ratios = m_df_dec / m_df
        R_dec = R * decontamination_ratios
        M_major = m_df.apply(keep_max, axis=1)
        M_major[M_major!=0] = 'Major_GBC'
        M_major[M_major==0] = 'Other'
        M_major_dec = m_df_dec.apply(keep_max, axis=1)
        M_major_dec[M_major_dec!=0] = 'Major_GBC'
        M_major_dec[M_major_dec==0] = 'Other'

        data_major = M_major.values.flatten()
        data_major_dec = M_major_dec.values.flatten()

        data_R = R.values.flatten()
        data_R_dec = R_dec.values.flatten()
        data_m_df = m_df.values.flatten()
        data_m_df_dec = m_df_dec.values.flatten()
    
        fig = plt.figure()
        colors = {'Major_GBC': 'green', 'Other': 'red'}
        sns.scatterplot(x=data_m_df, y=data_R, hue=data_major, palette=colors, s=1)
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w', markersize=3, markerfacecolor=color, label=label)
                        for label, color in colors.items()]
        plt.legend(title='data_type')
        plt.title(f'Coverage threshold= {coverage_treshold}')
        plt.xlabel('# unique UMI supporting a CBC-GBC')
        plt.ylabel('median of Read supporting a CBC-GBC')
        fig.savefig(os.path.join(path_results, f'UMI_vs_Read_{coverage_treshold}.png'), dpi=300)

        fig = plt.figure()
        colors = {'Major_GBC': 'green', 'Other': 'red'}
        sns.scatterplot(x=np.repeat(list(range(m_df.shape[0])),m_df.shape[1]), y=data_R, hue=data_major, palette=colors, s=1)
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w', markersize=3, markerfacecolor=color, label=label)
                        for label, color in colors.items()]
        plt.legend(title='data_type')
        plt.title(f'Coverage threshold= {coverage_treshold}')
        plt.xlabel('Cell')
        plt.ylabel('median of Read supporting a CBC-GBC')
        fig.savefig(os.path.join(path_results, f'cell_reads{coverage_treshold}.png'), dpi=300)

        fig = plt.figure()
        colors = {'Major_GBC': 'green', 'Other': 'red'}
        sns.scatterplot(x=np.repeat(list(range(m_df.shape[0])),m_df.shape[1]), y=data_m_df, hue=data_major, palette=colors, s=1)
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w', markersize=3, markerfacecolor=color, label=label)
                        for label, color in colors.items()]
        plt.legend(title='data_type')
        plt.title(f'Coverage threshold= {coverage_treshold}')
        plt.xlabel('Cell')
        plt.ylabel('# unique UMI supporting a CBC-GBC')
        fig.savefig(os.path.join(path_results, f'cell_UMI{coverage_treshold}.png'), dpi=300)





##


#histogram of the variation in the UMi counts and GBC counts after decontamination for each coverage threshold
if UMI_GBC_DecontX_correction_percentage_histogram==True:
    corrections_perc=np.array(super_data['corrections_perc'])
    data= corrections_perc
    fig = plt.figure()
    labels = ['0', '20', '40', '60', '80', '100']
    bar_width = 0.3
    index = np.arange(len(labels))
    data1 = data[:,0]
    data2 = data[:,1]
    plt.bar(index, data1, bar_width, label='GBC')
    plt.bar(index + bar_width, data2, bar_width, label='UMI')
    plt.xlabel('coverage threshold')
    plt.ylabel('loss ratio after correction')
    plt.xticks(index + bar_width, labels)
    plt.legend()
    fig.savefig(os.path.join(path_results, 'Correction ratios.png'), dpi=300)


##
    

#Boxplot of GBC abundancy of removed GBC in each cell for different coverage filtering
if GBC_completely_removed_relevance_boxplot ==True:
    complete_correction = super_data['complete_correction']
    data=[complete_correction[0][1],complete_correction[1][1],complete_correction[2][1],complete_correction[3][1],complete_correction[4][1],complete_correction[5][1]]
    fig = create_boxplots(data, plot_title='GBC abundancy of removed GBC in each cell', y_label='GBC abundancy', positions=th_list)
    fig.savefig(os.path.join(path_results, 'Relevance_of_removed_GBCs.png'), dpi=300)


##
    
 
# Box plot of the median of the GBC abundance distribution of each cell over different coverage filtering
if median_GBC_abundance_boxplot==True:
    median_data = super_data['median_data']
    data = [median_data[0],median_data[20],median_data[40],median_data[60],median_data[80],median_data[100]]
    fig = create_boxplots(data, plot_title='Median of the GBCs abundances for each cell', y_label='GBC abundancy', positions=th_list)
    fig.savefig(os.path.join(path_results, 'median_GBCs.png'), dpi=300)


##
    
 
#Box plot of the effect of the Decontx on the Major GBC and contaminated GBC for each cell over different coverage filtering
if DecontX_efficiency_of_decontamination_box_plot==True:

    #create_boxplots(data_list, plot_title, y_label, colors=None, positions=[0, 20, 40, 60, 80, 100])
    data=[]
    for i in range(len(decontamination_efficency_data['C'])): 
        data.append(decontamination_efficency_data['C'][i])
        data.append(decontamination_efficency_data['C_dec'][i])
    positions = [12, 12, 24, 24, 36, 36, 48, 48, 60, 60]
    #positions = [-1,19,39,59,79,99,1,21,41,61,81,101]
    title = 'Contamination count before and after decontamination for each cell'
    y_ax='Contamination count'
    fig = create_boxplots(data_list=data, plot_title=title, y_label=y_ax, colors=['r']+ ['b'], positions=positions )
    fig.savefig(os.path.join(path_results, 'CvsC.png'), dpi=300)
    

    data = decontamination_efficency_data['C/GBC']
    title = 'Ratio of Contamination percentage and major GBC percentage before decontamination for each cell'
    y_ax='Contamination % / major GBC %'
    fig = create_boxplots(data_list=data, plot_title=title, y_label=y_ax, positions=th_list )
    fig.savefig(os.path.join(path_results, 'C_GBC.png'), dpi=300)

    data = decontamination_efficency_data['C_dec/GBC_dec']
    title = 'Ratio of Contamination percentage and major GBC percentage after decontamination for each cell'
    y_ax='Contamination % / major GBC %'
    fig = create_boxplots(data_list=data, plot_title=title, y_label=y_ax, positions=th_list )
    fig.savefig(os.path.join(path_results, 'C_dec_GBC_dec.png'), dpi=300)

    data = decontamination_efficency_data['GBC_dec/GBC']
    title = 'Ratio of the major GBC percentage after and before decontamination for each cell'
    y_ax='major decontaminated GBC % / major GBC %'
    fig = create_boxplots(data_list=data, plot_title=title, y_label=y_ax, positions=th_list)
    fig.savefig(os.path.join(path_results, 'GBC_dec_GBC.png'), dpi=300)

    data = decontamination_efficency_data['C_dec/C']
    title = 'Ratio of Contamination percentage after and before decontamination for each cell'
    y_ax=' decontaminated Contamination % / Contamination %'
    fig = create_boxplots(data_list=data, plot_title=title, y_label=y_ax, positions=th_list )
    fig.savefig(os.path.join(path_results, 'C_dec_C.png'), dpi=300)

if loss_good_read_boxplot==True:

    #fig, axs = plt.subplots(1, 3, figsize=(15, 5))

    fig = plt.figure()
    data = super_data['loss_good_read']
    fig = create_boxplots(data, plot_title='Good reads loss after decontX', y_label='number of reads', positions=th_list)
    fig.savefig(os.path.join(path_results, 'Loss_good_read.png'), dpi=300)

    fig = plt.figure()
    data = super_data['loss_good_UMI']
    fig = create_boxplots(data, plot_title='Good UMI perc loss after decontX', y_label='# good UMI loss / # UMI before DecontX', positions=th_list)
    fig.savefig(os.path.join(path_results, 'Loss_UMI_perc.png'), dpi=300)

    fig = plt.figure()
    data = super_data['change_in_GBC']    
    sns.barplot(x=[0, 20, 40, 60, 80, 100], y=data)
    plt.xlabel('Coverage threshold')
    plt.ylabel('variation of major GBC %')
    plt.title('Percentage of the variation of the major GBC after DecontX')
    fig.savefig(os.path.join(path_results, 'variation_GBC.png'), dpi=300)