#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 10:54:17 2018

@author: ericlberlow
"""
#%%
'''
This script compares the distribution of keyword tags for AI books across different time periods.
1. add AI dummuy variable for all books with AI concept tag
2. add time periods in ai history
3. compute keyword tag distributions for each time period
4. merge into 1 table - create one col of all tags in master list
5. stack plots vertically - tags sorted alphabethiclly - to see different tag 'signatures'

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

df = pd.read_excel(infile, sheet_name='Nodes') # read nodes file

# add column for if AI is present or not in concepts list
df['concept_list'] = df['concepts'].str.split('|').apply(lambda x: [s.strip() for s in x]) # split tags and remove spaces
df['AI'] = df['concept_list'].apply(lambda x: True if 'AI' in x else False)

df = df[df['AI']==True]

#%%   #################### 

# add time periods for each book 
tdf = pd.read_excel(timeperiods)[['year', 'time_period']]

df = df.merge(tdf, on='year', how='inner')


#%%   #################### 
# build dataframe of keyword  counts for a given time period

def buildTagHistDf (df, p, col='keywords'):
    prows = df['time_period'] == p  # boolean of all rows of that period
    totBooks = prows.sum()
    tagDict = {}
    tagLists = df[col][prows].str.split('|')  # NOTE - index by boolean prows to subset rows
    tagLists = tagLists.apply(lambda x: [tag.strip(' ') for tag in x]) # strip empty spaces for each item in each list
    tagLists = tagLists.apply(lambda x: [tag for tag in x if tag != 'artificial intelligence']) # remove artificial intelligence tag
    tagHist = OrderedDict(Counter([t for tags in tagLists for t in tags if t is not '']).most_common()) #excludes rows with no data
    tagDict[col] = list(tagHist.keys()) # list of tags
    tagDict['count_'+p] = list(tagHist.values()) # list of counts
    tagdf = pd.DataFrame(tagDict) # convert dict to dataframe of tags and counts
    tagdf['pct_'+p] = tagdf['count_'+p].apply(lambda x: np.round((100*(x/totBooks)),2)) #convert counts to %
    tagdf.sort_values(by='pct_'+p, ascending=False, inplace=True) #sort
    #tagdf = tagdf[tagdf['pct_'+p]>=10] # keep tags that are in at least 10% of the books
    tagdf = tagdf.head(10) #keep top 10 tags
    return tagdf[[col, 'pct_'+p]]


#%%   #################### 
# get list of time periods
periods = list(df['time_period'].unique())


# create a list of keyword count dataframes - one for each time period
tag_dfs = [buildTagHistDf(df, p) for p in periods]


# merge all the tables into one with master keyword list with a column of counts for each period
tagdf = tag_dfs[0].merge(tag_dfs[1], on='keywords', how='outer')\
                  .merge(tag_dfs[2], on='keywords', how='outer')\
                  .merge(tag_dfs[3], on='keywords', how='outer')\
                  .merge(tag_dfs[4], on='keywords', how='outer')\
                  .merge(tag_dfs[5], on='keywords', how='outer')\
                  .merge(tag_dfs[6], on='keywords', how='outer')
                  
tagdf.fillna(0, inplace=True) # replace empty keyword counts with 0

# melt dataset into keywords and counts by time period

tagmelt = tagdf.melt(id_vars=['keywords'], var_name='time_period', value_name='percent')
tagmelt['Time Period'] = tagmelt['time_period'].apply(lambda x: x.split('_')[1]) # split count lable to extract time period



#%%   
## make tag distribution bar charts for each time period

tag_bars = alt.Chart(tagmelt, height=500, width=150).mark_bar().encode(
    y=alt.Y("keywords:O", 
            #sort=alt.EncodingSortField(field="percent:Q", op="values", order="ascending"),
            axis=alt.Axis(title='Top Keywords', 
                          grid=True,
                          )                        
            ),          
    x=alt.X("percent:Q",
            #scale=alt.Scale(domain =[-1.5, 1.5]),
            axis=alt.Axis(title='Percent of AI Books', 
                          grid=False)
            ),
    color=alt.Color('keywords:N', 
                    scale=alt.Scale(range=Colors), 
                    legend=None
                    )
  ).facet(
          column='Time Period:N')


tag_bars.save(datapath+'AI_taghists.html')

#tag_bars.serve()  ## launch html in browser - for Spyder

