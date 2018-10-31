#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
@author: ericlberlow
"""

#%%

import os.path
import pandas as pd
from ast import literal_eval  # to interpret column list values as list
#import numpy as np


# Define input and output file paths
dictpath = "."
datapath = "Results"

netfilename = os.path.join(datapath, "scifi_network_IDF_201810.xlsx")
outname = os.path.join(datapath, "scifi_network_IDF_cleaned2.xlsx")


#%%
# read network xlsx with nodes and links sheets
netdf = pd.ExcelFile(netfilename) 
ndf = netdf.parse('Nodes')
ldf = netdf.parse('Links')

#%% add shorter cluster titles
ndf['top_tags']= ndf['top_tags'].apply(literal_eval) # read this as a list not string.
# shorter cluster name - get top 5 tags and concatenate into string 
ndf['keyword theme'] = ndf['top_tags'].apply(lambda x: ','.join(x[:3])) 
ndf.drop(['top_tags'], axis=1, inplace=True)

#%% add column for if AI is present or not in concepts list
ndf['concept_list'] = ndf['concepts'].str.split('|').apply(lambda x: [s.strip() for s in x]) # split tags and remove spaces
ndf['AI'] = ndf['concept_list'].apply(lambda x: "AI" if 'AI' in x else "")


#%% add historic AI time periods

def add_time_period (x):
    if (x >=1952) and (x <=1956):
        time="1952-1956 Birth of AI"
    elif (x>1956) and (x<=1973):
        time="1957-1973 Golden Years"
    elif (x>1973) and (x<=1980):
        time="1974-1980 1st AI Winter"
    elif (x>1980) and (x<=1987):
        time="1981-1987 Expert Systems"
    elif (x>1987) and (x<=1993):
        time="1988-1998 2nd AI Winter"
    elif (x>1993) and (x<=2011):
        time="1994-2011 Quiet Progress"
    elif (x>2011):
        time="2012-2017 BigData - DeepLearning"
    else:
        time=""
    return time

ndf['time period'] = ndf['year'].apply(lambda x: add_time_period(x))   

#%% reorder and rename cols

#re-order columns
colOrder = ['keywords','concepts','AI', 'time period',
            'author_tags',  'year', 
            'log_n_reviews', 'n_reviews',
            'n_keywords', 'genre_tags', 
            'author', 'title', 'year(s)_published',
            'plot', 'url','keyword list','concept_list',
            'label', 'id', 'Cluster',
            'keyword theme','cluster_name', 
            'Degree', 'ClusterBridging',
            'ClusterArchetype',
            ]
    
ndf = ndf[colOrder]

#rename columns
renameDict = {'cluster_name': 'keyword theme (long)',
              'ClusterArchetype': 'theme centrality',
              'ClusterBridging': 'theme bridging',
              'log_n_reviews': 'log(reviews)', 
              'n_reviews': 'reviews',
              'n_keywords': 'number of keywords',
              'year(s)_published': 'years(s) published'
              }

ndf.rename(columns=renameDict, inplace=True)




#%%


#write ouit network file excel file with 2 sheets
writer = pd.ExcelWriter(outname)
ndf.to_excel(writer,'Nodes', index=False)
ldf.to_excel(writer,'Links', index=False)
writer.save() 
print('writing network excel files')





