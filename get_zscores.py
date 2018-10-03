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
    centered_pctl = (pctl_obs - 0.5)/0.5 # center the percentile at 50th pctl = 0
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

zdf = zdf[(zdf['books_published']>=10) & ((zdf['year']>=1950) & (zdf['year'] < 2017))] # trim years prior to 1950 and fewer than 10 books.

yrdf = pd.DataFrame({'year': range(zdf['year'].min(), zdf['year'].max()+1)}) # make dataframe with complete years
zdf = zdf.merge(yrdf, on='year', how='outer')  #merge data to pad missing years
zdf.sort_values(by='year', inplace=True) 


#%%   #################### 
#compute 3 yr rolling avg for each statistic
 
rollCols = ['obs_frac_AI','z_frac_AI', 'pctl_frac_AI','centered_pctl_frac_AI', 'books_published' ]
for col in rollCols: 
    zdf['roll_'+col] = zdf[col].rolling(3, min_periods=3, center=True).mean()


#%%   #################### 
#clean up dataset and reorder cols - write excel file to play with. 
orderCols = ['year','books_published', 'obs_frac_AI', 'z_frac_AI',  'pctl_frac_AI', 'centered_pctl_frac_AI', 
            'roll_books_published', 'roll_obs_frac_AI', 'roll_z_frac_AI','roll_pctl_frac_AI','roll_centered_pctl_frac_AI']

zdf = zdf[orderCols]
zdf['top_ref']= 0.75
zdf['bottom_ref'] = -0.75
zdf.fillna(0, inplace=True)
zdf.to_excel(datapath + "AI_zscores.xlsx", index=False)

#%% #############
#  ADD CHART ANNOTATIONS FOR TIME PERIODS

## Birth ##
birth_x = list(range(1952, 1957))  
birth_y = [1.5]*len(birth_x)
birth_label = ["Birth of AI"]*len(birth_x)
birth_df = pd.DataFrame({'year':birth_x, 'y': birth_y, 'period': birth_label})

## Golden Years ##
golden_x = list(range(1956, 1974))  
golden_y = [1.6]*len(golden_x)
golden_label = ["Golden Years"]*len(golden_x)
golden_df = pd.DataFrame({'year':golden_x, 'y': golden_y, 'period': golden_label})

## First AI Winter ##
winter1_x = list(range(1973,1981))
winter1_y = [1.5]*len(winter1_x)
winter1_label = ["1st AI Winter"]*len(winter1_x)
winter1_df = pd.DataFrame({'year':winter1_x, 'y': winter1_y, 'period': winter1_label})

## Expert System Boom  ##
boom_x = list(range(1980, 1988))
boom_y = [1.6]*len(boom_x)
boom_label = ["Expert Systems"]*len(boom_x)
boom_df = pd.DataFrame({'year':boom_x, 'y': boom_y,  'period': boom_label})

## Second AI Winter ##
winter2_x = list(range(1987,1994))
winter2_y = [1.5]*len(winter2_x)
winter2_label = ["2nd AI Winter"]*len(winter2_x)
winter2_df = pd.DataFrame({'year':winter2_x, 'y': winter2_y, 'period': winter2_label})


 ## Quiet Years ##
quiet_x = list(range(1993,2011))
quiet_y = [1.6]*len(quiet_x)
quiet_label = ["Low Profile Progress"]*len(quiet_x)
quiet_df = pd.DataFrame({'year':quiet_x, 'y': quiet_y, 'period':quiet_label})

## Big Data Bump ##
bigdata_x = list(range(2011,2017))
bigdata_y = [1.5]*len(bigdata_x)
bigdata_label = ["Big Data Boom"]*len(bigdata_x)
bigdata_df = pd.DataFrame({'year':bigdata_x, 'y': bigdata_y, 'period': bigdata_label })

annotate_df = pd.concat([birth_df, golden_df, winter1_df, boom_df, winter2_df, quiet_df, bigdata_df], sort=False)
annotate_df.sort_values(by='year', ascending=True, inplace=True)

#%% ##########
## MAKE CHARTS
##############
#plot rolling mean of standardized fraction of AI books over time - color by the avg percentile of that value show significance.

color_palette = ['#355fdc', '#FFC300'] # end points of color range 
line_palette = ['#1a1a1a','#1a1a1a','#cccccc','#cccccc','#cccccc','#cccccc','#cccccc']

# plot number of books published per year vs time
books_v_time = alt.Chart(zdf, width=1000, height=150).mark_circle().encode(
    x=alt.X('year:O',
            axis=alt.Axis(title=None, labels=True, grid=False)
            ),
    y=alt.Y('books_published:Q',
            axis=alt.Axis(title='SciFi Books Published', 
                          grid=False)
            ),
    color=alt.Color('roll_centered_pctl_frac_AI', 
                    scale=alt.Scale(range=color_palette), 
                    legend=None),
    size = alt.value(50)
    )


# plot rolling average zscore of frac AI books  vs time

ai_v_time = alt.Chart(zdf, width=1000).mark_bar().encode(
    x=alt.X("year:O",
            axis=alt.Axis(title='Year', 
                          grid=False)
            ),          
    y=alt.Y("roll_z_frac_AI:Q",
            scale=alt.Scale(domain =[-1.8, 1.8]),
            axis=alt.Axis(title='AI Books Relative to Expected', 
                          grid=False)
            ),
    color=alt.Color('roll_centered_pctl_frac_AI', 
                    scale=alt.Scale(range=color_palette), 
                    # altair converts this into a smooth color gradient because the y axis is numeric
                    legend=None
                    )
  )
## add zscore significance ref lines

sig_band = alt.Chart(zdf).mark_area(opacity=0.2).encode(
    x='year:O',
    y='top_ref',
    y2='bottom_ref',
    color = alt.value('#cccccc')
    
)


# plot timeline annotations - lines 
annotate = alt.Chart(annotate_df, width=1000).mark_line().encode(
        x="year:O",
        y=alt.Y("y",
            scale=alt.Scale(domain =[-1.8, 1.8])
                ),
        color=alt.Color('period', 
                scale=alt.Scale(range=line_palette),  
                # grey black nominal palette for line categories
                legend=None,
                ),
        size=alt.value(5)
        )

# add text labels to annotations 
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
    (alt.datum.year == 2011)  
)

# multiple chart layout  and save chart
ai_chart = ai_v_time + sig_band + annotate + text
charts = books_v_time & ai_chart
charts = charts.configure_view(strokeOpacity=0) # hide the thin outline of each chart 

charts.save(datapath+'annotated_charts.html')
#charts.serve()  ## launch html in browser - for Spyder
#charts.display()  ## for jupyter notebooks


