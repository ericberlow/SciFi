#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 12 07:15:16 2018

@author: ericlberlow
"""
import pandas as pd
import numpy as np
from collections import Counter, OrderedDict

pd.set_option('display.expand_frame_repr', False) # expand display of data columns if screen is wide

# Define input and output file paths
datapath = "Results/"
infile = (datapath + "scifi_network_noIDF_201807.xlsx")

#%%   #################### 
print('reading nodes files')
df = pd.read_excel(infile, sheet_name='Nodes')[['author','title','year','n_reviews','keywords', 'concepts']] # read nodes file

# add column for if AI is present or not in concepts list
df['concept_list'] = df['concepts'].str.split('|').apply(lambda x: [ss.strip() for ss in x])
df['AI'] = df['concept_list'].apply(lambda x: True if 'AI' in x else False)

# test on one year:
yeardf = df[df['year']==1975]

#%%   #################### 

# get fraction of books with AI tag
def get_frac (group, attr='AI'):
   nbooks = group[attr].count()
   n_tag = group[attr].sum()
   frac_tag = n_tag/nbooks
   return frac_tag

# compute zscore of observed value vs mean and std of sampled distribution
def compute_zscore(obs, smpl_mean, smpl_std):
    zscore = (obs-smpl_mean)/smpl_std
    return zscore

# for a group, sample the same nbooks randomly from the larger df
# for each sample, compute the fraction of books with AI
# repeat 1000 times and compute the mean and std of the frac AI books across random samples
# compute zscore of the observed group frac compared to mean and std of 1000 random samples of same size    

def get_sampled_zscore (group, df, attr='AI',niter=1000):
    sample_fracs = []
    nbooks = group[attr].count()
    obs_frac = get_frac(group, attr)
    for i in range (0, niter):
        smpl_df = df.sample(nbooks) # get random sample of same size as the group
        smpl_frac_ai = get_frac(smpl_df, attr=attr) # get frac ai books in the sample
        sample_fracs.append(smpl_frac_ai) # compile list of frac_ai for all samples
        print("%.2f AI books in sample %d of %d books"%(smpl_frac_ai, i, nbooks))
    frac_series = pd.Series(sample_fracs)  #convert list to series
    mean_smpl_frac = frac_series.mean() # compute mean frac ai for 1000 samples
    std_smpl_frac = frac_series.std() # cmopute std frac ai for the 1000 samples
    zscore = compute_zscore(obs_frac, mean_smpl_frac, std_smpl_frac) # compute zscore of observed group frac ai
    return obs_frac, zscore


#%%   #################### 

frac_ai, zscore = get_sampled_zscore(yeardf, df) # get zscore of observed vs expected  by chance from 1000 random samples

frac_ai, zscore

#%%   #################### 

#TODO: my idea was to group by year and apply the 'get_sampled_zscore' funtion to each year.
#I'm a little stuck on how best to do this... and end up with a datafram of yr, frac_ai, zscore_ai
'''
years = df.groupby(['year']) # group by year
fracs, zscores = get_sampled_zscore(years, df, attr='AI', niter=1000)
'''

