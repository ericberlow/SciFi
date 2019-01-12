#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 12 07:15:16 2018

@author: ericlberlow
"""
#%%
### What this script does
## 1 - summarizes total books and fraction of AI books per year
## 2 - smooths the trend with a 3 yr rolling average of the frac AI books per year
## 3 - computes a sampled z-score for that observed frac AI books per year by
##      randomly sampling the same number of books for that year from the entire dataset 
##      computing the frac AI books per sample 
##      repeating 1000 times to get a distribution of expected frac AI books for that sample size
##      compute a z_score for the frac AI books for that year (i.e. # standard deviations from the expected mean)
##      compute the percentile score of the observed frac AI books (i.e., what % of random trials are less than the observed value)
## 4 - Plots trends of AI publishing over time 
##      Overlays historic events on the trend. 

## The z_score answers the question - 
#       - what is the frac AI books relative to average expected by chance (divided by the std dev of chance values)
## The percentile answers the questions :
##      - how surprising is the observed frac AI?
##      - what fraction of the trials had a lower frac AI value than the observed one

#%%

import pandas as pd
import altair as alt
import numpy as np

pd.set_option('display.expand_frame_repr', False) # expand display of data columns if screen is wide

# Define input and output file paths
datapath = "Results/"
infile = (datapath + "scifi_network_noIDF_201810.xlsx")
timeperiods = "AI_time_periods.xlsx"


#%%   #################### 
print('reading nodes files')
df = pd.read_excel(infile, sheet_name='Nodes')[['author','title','year','n_reviews','keywords', 'concepts']] # read nodes file

# add column for if AI is present or not in concepts list
df['concept_list'] = df['concepts'].str.split('|').apply(lambda x: [s.strip() for s in x]) # split tags and remove spaces
df['AI'] = df['concept_list'].apply(lambda x: True if 'AI' in x else False)

# filter out years prior to beginning of AI
df = df[df['year']>=1950]
df = df[['year', 'AI']].sort_values(by='year')

#%%   #################### 
#summarize for each year -  total books, total ai books, frac ai books
def sumstats (group, attr='AI'):
    d = {} # dictionary to hold results
    d['n_books'] = len(group) # length of group (total books)
    d['n_'+attr] =  group[attr].sum() #sum all 1's in boolean
    d['frac_'+attr] = d['n_'+attr]/d['n_books'] # fraction books tagged with AI
    df = pd.DataFrame(d, index=[0]) # make dataframe of summary stats - need to pass index to dataframe
    return df
    
yrdf = df.groupby(['year']).apply(lambda x: sumstats(x, attr='AI'))
yrdf.reset_index(level='year', inplace=True)  # move year from index to column
yrdf.reset_index(drop=True, inplace=True) # reset index which was 0

#%%   #################### 

#compute 3 yr rolling avg for each statistic
rollCols = ['n_books','n_AI', 'frac_AI']
for col in rollCols: 
    yrdf['roll_'+col] = yrdf[col].rolling(3, min_periods=3, center=True).mean()

#round decimals   
roundCols = ['frac_AI', 'roll_n_books', 'roll_n_AI', 'roll_frac_AI']
for col in roundCols: 
    yrdf[col] = yrdf[col].apply(lambda x: round(x, 2))
  
yrdf.fillna(0, inplace=True) # rolling mean on ends (1949 and 2018) is NaN.
yrdf['roll_n_books'] = yrdf['roll_n_books'].apply(lambda x: int(x)) #convert rolling mean to int to randomly sample int books.

#%%   #################### 
# get sampled z-score and percentile for observed rolling frac AI books in each year
# answers the question "what is the likelihood that my observed frac of AI books could have been observed by chance?"" 
# for each year, sample the same nbooks from the full dataset as the rolling mean n books for that year 
# for each sample, compute the fraction of books with AI
# repeat 1000 times and compute the mean and std of the frac AI books across random samples
# compute zscore of the observed group frac compared to mean and std of 1000 random samples of same size
# compute the percentile of the observed frac    

# get fraction of books with AI tag
def get_frac (group, attr='AI'):
   nbooks = group[attr].count() # total books - length of boolean array 
   n_tag = group[attr].sum() # number of books tagged with AI
   frac_tag = n_tag/nbooks # fraction books tagged with AI
   return frac_tag

# compute zscore of observed value vs mean and std of sampled distribution
def compute_zscore(obs, smpl_mean, smpl_std):
    zscore = (obs-smpl_mean)/smpl_std
    return zscore


# note - by using group[col] this function adds new col to the dataframe
def get_sampled_zscore (group, df=df, attr='AI',niter=1000):
    sample_frac_list = []
    nbooks = group['roll_n_books'].values[0] # rolling mean of total books for the year
    obs_frac = group['roll_frac_AI'].values[0] # rolling mean of frac books for the year
    for i in range (0, niter):
        if nbooks > 0:
            smpl_df = df.sample(nbooks) # get random sample of same size as the group
            smpl_frac_ai = get_frac(smpl_df, attr=attr) # get frac ai books in the sample
            sample_frac_list.append(smpl_frac_ai) # compile list of frac_ai for all samples
            print("%.2f AI books in sample %d of %d books in year %d"%(smpl_frac_ai, i, nbooks, group['year'].values[0]))
        else:
            smpl_frac_ai = np.nan # assign no data for frac ai books in the sample
            sample_frac_list.append(smpl_frac_ai) # compile list of frac_ai for all samples

    sample_fracs = pd.Series(sample_frac_list).sort_values()  #convert list of sample fracs to series
    group['pctl_frac_'+attr] = sample_fracs.searchsorted(obs_frac)[0]/len(sample_fracs) #get percentile of the obs value
    #group['cntrd_pct_obs_frac_'+attr] = (group['pctl_obs_frac_'+attr] - 0.5)/0.5 # center the percentile at 50th pctl = 0
    mean_smpl_frac = sample_fracs.mean() # compute mean frac ai for 1000 samples
    std_smpl_frac = sample_fracs.std() # cmopute std frac ai for the 1000 samples
    group['z_frac_'+attr] = compute_zscore(obs_frac, mean_smpl_frac, std_smpl_frac) # compute zscore of observed group frac ai
    return group  #returns a dataframe with new computed cols added to original ones


#%%   #################### 
# # group by year and compute scores 
zdf = yrdf.groupby(['year']).apply(get_sampled_zscore) # adds extra computed columns to original ones. 


#%%   #################### 
# trim end years (1949 had NaN, 2016-2018 had unusually low n books)
zdf = zdf[(zdf['year']>1949) & (zdf['year'] < 2016)] 

# make new dataframe with complete sequence of years 1950-2015
yrfill_df = pd.DataFrame({'year': range(zdf['year'].min(), zdf['year'].max()+1)}) 
zdf = zdf.merge(yrfill_df, on='year', how='outer')  #merge data to pad missing years
zdf.sort_values(by='year', inplace=True) 


#%%   #################### 
#clean up dataset and reorder cols - write excel file to play with it. 
orderCols = ['year', 'n_books', 'n_AI', 'frac_AI', 
             'roll_n_books', 'roll_n_AI', 'roll_frac_AI', 
             'pctl_frac_AI', 'z_frac_AI']

zdf = zdf[orderCols]
zdf['top_ref']= 1
zdf['bottom_ref'] = -1
#zdf.fillna(0, inplace=True)
zdf.sort_values(by='year', inplace=True)
zdf.to_excel(datapath + "AI_zscores.xlsx", index=False)

#%% #############
#  get chart annotations for time periods (created in AI_timeline_annotations.py)
annotate_df = pd.read_excel(timeperiods)


#%% ##########
## MAKE CHARTS
# plot zscore of 3 yr rolling mean fraction of AI books over time 
# color by significance - or the percentile score of the observed value.
##########

color_palette = ['#355fdc', '#FFC300'] # end points of color range 
line_palette = ['#1a1a1a','#1a1a1a','#cccccc','#cccccc','#cccccc','#cccccc','#cccccc'] # black, grey

# plot number of books published per year vs time
nbooks_v_time = alt.Chart(zdf, width=1000, height=150).mark_circle().encode(
    x=alt.X('year:O',
            axis=alt.Axis(title=None, labels=False, ticks=False, grid=False)
            ),
    y=alt.Y('roll_n_books:Q',
            axis=alt.Axis(title='SciFi Books Published', 
                          grid=False)
            ),
    order= 'year',
    color=alt.value('#808080')    
 #   size = alt.value(5)
    )

# plot number of AI books published per year vs time
fracAI_v_time = alt.Chart(zdf, width=1000, height=150).mark_circle().encode(
    x=alt.X('year:O',
            axis=alt.Axis(title=None, labels=False, ticks=False, grid=False)
            ),
    y=alt.Y('roll_n_AI:Q',
            axis=alt.Axis(title='SciFi Books Published', 
                          grid=False)
            ),
    order= 'year',
    color=alt.Color('pctl_frac_AI', 
                    scale=alt.Scale(range=color_palette), 
                    legend=None)
    )

# overlay total books and total AI books per yer  vs time
books_v_time = nbooks_v_time + fracAI_v_time
#books_v_time = nbooks_v_time  

# plot rolling average zscore of frac AI books  vs time
ai_v_time = alt.Chart(zdf, width=1000).mark_bar().encode(
    x=alt.X("year:O",
            axis=alt.Axis(title='Year', 
                          grid=False)
            ),          
    y=alt.Y("z_frac_AI:Q",
            scale=alt.Scale(domain =[-1.5, 1.5]),
            axis=alt.Axis(title='AI Books Relative to Expected', 
                          grid=False)
            ),
    color=alt.Color('pctl_frac_AI', 
                    scale=alt.Scale(range=color_palette), 
                    # altair converts this into a smooth color gradient because the y axis is numeric
                    legend=(alt.Legend(title='Percentile'))
                    )
  )

## add zscore significance band ref lines
sig_band = alt.Chart(zdf).mark_area(opacity=0.2).encode(
    x='year:O',
    y='top_ref',
    y2='bottom_ref',
    color = alt.value('#696969')
)


# plot timeline annotations - lines
annotate = alt.Chart(annotate_df, width=1000).mark_line().encode(
        x="year:O",
        y=alt.Y("y",
            scale=alt.Scale(domain =[-1.5, 1.5])
                ),
        color=alt.Color('period', 
                scale=alt.Scale(range=line_palette),  
                # grey black nominal palette for line categories
                legend=None,
                ),
        size=alt.value(5)
        )

# add text labels to annotations by plotting  labels for specific points
text = alt.Chart(annotate_df).mark_text(
    align='left',
    baseline='middle',
    fontSize=10,
    dy=-10
    ).encode(
            x='year:O',
            y='y',
            text='period' ## use the time period as the labels 
    ).transform_filter(   ## only select one year from each period to render the label ##
    (alt.datum.year == 1952)| (alt.datum.year == 1962)| (alt.datum.year == 1974)|
    (alt.datum.year == 1981)| (alt.datum.year == 1988)| (alt.datum.year == 1999)|
    (alt.datum.year == 2012)  
)

# multiple chart layout  and save chart
ai_chart = ai_v_time + sig_band + annotate + text
charts = books_v_time & ai_chart
charts = charts.configure_view(strokeOpacity=0) # hide the thin outline of each chart 

charts.save(datapath+'annotated_charts_v4.html')
#charts.serve()  ## launch html in browser - for Spyder
#charts.display()  ## for jupyter notebooks


