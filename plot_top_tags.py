#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 10:54:17 2018

@author: ericlberlow
"""
#%%
'''
This script compares the distribution of top keywords for all sci fi books by decade
1. add decade time periods for grouping
2. compute keyword tag distributions for each time period
4. merge into 1 table - create one col of all tags in master list
5. stack plots vertically - tags sorted by decade - to see different keyword 'signatures' by decade

'''

#%%
import pandas as pd
import numpy as np
from collections import Counter, OrderedDict
import altair as alt
Colors = ['#2aadbf','#f06b51', '#fbb44d', '#616161','#334e7d','#1a7480','#539280'] # blue, orange, yellow, gray, dark blue, ocean green, light green
pd.set_option('display.expand_frame_repr', False) # expand display of data columns if screen is wide


# Define input and output file paths
dictpath = "."
datapath = "Results/"
infile = (datapath + "scifi_network_IDF_201810.xlsx")
timeperiods = ("AI_time_periods.xlsx")

#%%   #################### 
print('reading nodes files')
keepcols = ['author', 'title', 'year', 'n_reviews', 'keywords', 'concepts', 'id']

df = pd.read_excel(infile, sheet_name='Nodes')[keepcols] # read nodes file


#%%   #################### 

# add decade for each book
df['decade']= (df['year']//10)*10  #add decade column

'''
# add column for if AI is present or not in concepts list
df['concept_list'] = df['concepts'].str.split('|').apply(lambda x: [s.strip() for s in x]) # split tags and remove spaces
df['AI'] = df['concept_list'].apply(lambda x: True if 'AI' in x else False)

df = df[df['AI']==True]
'''

#%%   #################### 
# build dataframe of keyword  counts for a each time period

def buildTagHistDf (df, p, col='keywords', period='decade'):
    prows = df[period] == p  # boolean of all rows of that period
    totBooks = prows.sum()
    tagDict = {} # empty dictionary to hold results
    tagLists = df[col][prows].str.split('|')  # NOTE - index by boolean prows to subset rows
    tagLists = tagLists.apply(lambda x: [tag.strip(' ') for tag in x]) # strip empty spaces for each item in each list
    #tagLists = tagLists.apply(lambda x: [tag for tag in x if tag != 'artificial intelligence']) # remove artificial intelligence tag
    tagHist = OrderedDict(Counter([t for tags in tagLists for t in tags if t is not '']).most_common()) #excludes rows with no data
    tagDict[col] = list(tagHist.keys()) # list of tags
    tagDict['count_'+str(p)] = list(tagHist.values()) # list of counts
    tagdf = pd.DataFrame(tagDict) # convert dict to dataframe of tags and counts
    tagdf['pct_'+str(p)] = tagdf['count_'+str(p)].apply(lambda x: np.round((100*(x/totBooks)),2)) #convert counts to %
    tagdf.sort_values(by='pct_'+str(p), ascending=False, inplace=True) #sort
    #tagdf = tagdf[tagdf['pct_'+p]>=10] # keep tags that are in at least 10% of the books
    tagdf = tagdf.head(10) #keep top 10 tags
    return tagdf[[col, 'pct_'+str(p)]]  # note need to convert period to string to make name


#%%   #################### 
# get list of time periods

#periods = list(df['time_period'].unique())
periods = list(df['decade'].unique()) 

# create a list dataframes - one for each time period - of keyword count
tag_dfs = [buildTagHistDf(df, p) for p in periods]


# merge all the tables into one with master keyword list with a column of counts for each period
'''
tagdf = tag_dfs[0].merge(tag_dfs[1], on='keywords', how='outer')\
                  .merge(tag_dfs[2], on='keywords', how='outer')\
                  .merge(tag_dfs[3], on='keywords', how='outer')\
                  .merge(tag_dfs[4], on='keywords', how='outer')\
                  .merge(tag_dfs[5], on='keywords', how='outer')\
                  .merge(tag_dfs[6], on='keywords', how='outer')
 '''                 
tagdf = tag_dfs[0]                  
for i in range(len(tag_dfs)-1):
    tagdf = tagdf.merge(tag_dfs[i+1], on='keywords', how='outer')
                  
tagdf.fillna(0, inplace=True) # replace empty keyword counts with 0

#%%   #################### 

# melt dataset into keywords and counts by time period

tagmelt = tagdf.melt(id_vars=['keywords'], var_name='time_period', value_name='percent')
tagmelt['Time Period'] = tagmelt['time_period'].apply(lambda x: x.split('_')[1]) # split count lable to extract time period
tagmelt.drop('time_period', axis=1, inplace=True)
# save dataset to excel
tagmelt.to_excel(datapath+"top_kwds_byDecade.xlsx", index=False)

#%%   
## make tag distribution bar charts for each time period

tag_bars = alt.Chart(tagmelt, height=500, width=75).mark_bar().encode(
    y=alt.Y("keywords:O", 
            #sort=alt.EncodingSortField(field="percent:Q", op="values", order="ascending"),
            axis=alt.Axis(title='Top Keywords', 
                          grid=True,
                          )                        
            ),          
    x=alt.X("percent:Q",
            #scale=alt.Scale(domain =[-1.5, 1.5]),
            axis=alt.Axis(title='% of Books', 
                          grid=False)
            ),
    color=alt.Color('keywords:N', 
                    scale=alt.Scale(range=Colors), 
                    legend=None
                    )
  ).facet(
          column='Time Period:Q')


tag_bars.save(datapath+'AI_taghists.html')

#tag_bars.serve()  ## launch html in browser - for Spyder

