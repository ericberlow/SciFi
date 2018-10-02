#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 12 07:15:16 2018

@author: ericlberlow
"""
import pandas as pd
import altair as alt
#import numpy as np

pd.set_option('display.expand_frame_repr', False) # expand display of data columns if screen is wide

# Define input and output file paths
datapath = "Results/"
infile = (datapath + "scifi_network_noIDF_201807.xlsx")

#%%   #################### 
print('reading nodes files')
df = pd.read_excel(infile, sheet_name='Nodes')[['author','title','year','n_reviews','keywords', 'concepts']] # read nodes file

# add column for if AI is present or not in concepts list
df['concept_list'] = df['concepts'].str.split('|').apply(lambda x: [s.strip() for s in x]) # split tags and remove spaces
df['AI'] = df['concept_list'].apply(lambda x: True if 'AI' in x else False)

df = df[df['year']>=1930]
df = df[['year', 'AI']].sort_values(by='year')



#%%   #################### 

# get fraction of books with AI tag
def get_frac (group, attr='AI'):
   nbooks = group[attr].count()  
   n_tag = group[attr].sum() # number of books tagged with AI
   frac_tag = n_tag/nbooks # fraction books tagged with AI
   return frac_tag

# compute zscore of observed value vs mean and std of sampled distribution
def compute_zscore(obs, smpl_mean, smpl_std):
    zscore = (obs-smpl_mean)/smpl_std
    return zscore

# for a group, sample the same nbooks randomly from the larger df
# for each sample, compute the fraction of books with AI
# repeat 1000 times and compute the mean and std of the frac AI books across random samples
# compute zscore of the observed group frac compared to mean and std of 1000 random samples of same size    

def get_sampled_zscore (group, df=df, attr='AI',niter=1000):
    sample_frac_list = []
    nbooks = group[attr].count()
    obs_frac = get_frac(group, attr)
    for i in range (0, niter):
        smpl_df = df.sample(nbooks) # get random sample of same size as the group
        smpl_frac_ai = get_frac(smpl_df, attr=attr) # get frac ai books in the sample
        sample_frac_list.append(smpl_frac_ai) # compile list of frac_ai for all samples
        print("%.2f AI books in sample %d of %d books in year %d"%(smpl_frac_ai, i, nbooks, group['year'].head(1)))
    sample_fracs = pd.Series(sample_frac_list).sort_values()  #convert list of sample fracs to series
    pctl_obs = sample_fracs.searchsorted(obs_frac)[0]/len(sample_fracs) #get percentile of the obs value
    centered_pctl = (pctl_obs - 0.5) # center the percentile at 50th pctl = 0
    mean_smpl_frac = sample_fracs.mean() # compute mean frac ai for 1000 samples
    std_smpl_frac = sample_fracs.std() # cmopute std frac ai for the 1000 samples
    z_frac = compute_zscore(obs_frac, mean_smpl_frac, std_smpl_frac) # compute zscore of observed group frac ai
    results = {'year': group['year'].values[0],  #pick first year of group 
               'obs_frac_'+attr: obs_frac,
               'z_frac_'+attr: z_frac,
               'books_published': nbooks,
               'pctl_frac_'+attr: pctl_obs,
               'centered_pctl_frac_'+attr: centered_pctl}
    return results  #returns a series of dictionaries



#%%   #################### 
#group by year and apply the 'get_sampled_zscore' funtion to each year.

zdict = df.groupby(['year']).apply(get_sampled_zscore)  # group by year and compute scores
zdf = pd.DataFrame(zdict.tolist())  # convert list of dictionaries and then to dataframe 

#%%   #################### 

zdf = zdf[zdf['books_published']>=10] # trim years that had fewer than 10 books.

yrdf = pd.DataFrame({'year': range(df['year'].min(), df['year'].max()+1)}) # make dataframe with complete years
zdf = zdf.merge(yrdf, on='year', how='outer')  #merge data to pad missing years
zdf.sort_values(by='year', inplace=True) 
zdf = zdf[zdf['year']>=1950] # all years before 1950 had <10 books.


#%%   #################### 
#compute 3 yr rolling avg for each statistic
 
rollCols = ['obs_frac_AI','z_frac_AI', 'pctl_frac_AI','centered_pctl_frac_AI', 'books_published' ]
for col in rollCols: 
    zdf['roll_'+col] = zdf[col].rolling(3, min_periods=2, center=True).mean()


#%%   #################### 
#clean up dataset and reorder cols - write excel file to play with. 
orderCols = ['year','books_published', 'obs_frac_AI', 'z_frac_AI',  'pctl_frac_AI', 'centered_pctl_frac_AI', 
            'roll_books_published', 'roll_obs_frac_AI', 'roll_z_frac_AI','roll_pctl_frac_AI','roll_centered_pctl_frac_AI']

zdf = zdf[orderCols]
zdf.fillna(0, inplace=True)
zdf.to_excel(datapath + "AI_zscores.xlsx", index=False)


#%% #######
#plot rolling mean of standardized fraction of AI books over time - color by the avg percentile of that value show significance.

color_palette = ['#355fdc', '#FFC300'] # end points of color range 

ai_v_time = alt.Chart(zdf).mark_bar().encode(
    x="year:O",
    y="roll_z_frac_AI:Q",
    color=alt.Color('roll_centered_pctl_frac_AI', scale=alt.Scale(range=color_palette), title='significance')
    )

books_v_time = alt.Chart(zdf).mark_circle().encode(
    x='year:O',
    y='roll_books_published:Q',
    color=alt.Color('roll_centered_pctl_frac_AI', scale=alt.Scale(range=color_palette), title='significance')
    )

charts = ai_v_time & books_v_time

#charts.serve()
charts.save(datapath+'bookcharts.html')
