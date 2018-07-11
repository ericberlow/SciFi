#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 09:01:15 2017

@author: ericlberlow
"""

#%%
import sys

#reload(sys)
#sys.setdefaultencoding('utf-8')
sys.path.append("../Tag2Network/tag2network")

import os.path
import pandas as pd
import numpy as np
from Tags.BuildKeywords import buildKeywords
from Network.BuildNetwork import buildTagNetwork
from collections import Counter, OrderedDict
import holoviews as hv
from bokeh.io import output_file, show
#from bokeh.io import save
from bokeh.plotting import reset_output
hv.extension('bokeh','matplotlib')
Colors = ['#2aadbf','#f06b51', '#fbb44d', '#616161','#334e7d','#1a7480','#539280'] # blue, orange, yellow, gray, dark blue, ocean green, light green


# Define input and output file paths
dictpath = "."
datapath = "Results"
termdictname = os.path.join(dictpath, "scifi_syndic_conceptdic.xlsx")
filename = os.path.join(datapath, "scifi_201807.txt") 
kwdname_IDF = os.path.join(datapath, "scifi_network_IDF_201807.xlsx")
kwdname_noIDF = os.path.join(datapath, "scifi_network_noIDF_201807.xlsx")
cncptname_IDF = os.path.join(datapath, "scifi_conceptNetwork_IDF_201807.xlsx")
cncptname_noIDF = os.path.join(datapath, "scifi_conceptNetwork_noIDF_201807.xlsx")


#plotfile = os.path.join(datapath, "scifi_plot_IDF_4-4-18.pdf")

#%%

# read text and keyword file
print ('reading text file')
df = pd.read_csv(filename, sep='\t', header=0, encoding='utf-8')
print ('data reading done')
df = df.fillna('')
df['year'] = df['year'].apply(pd.to_numeric) 
df = df[df['year']>=1850] # keep all books published since 1900
#df = df.iloc[0:500,:] #test with first 500 records
#%%

# read dictonary of search terms mapped to common terms (key is search term, value is unique common term)
sd_df = pd.read_excel(termdictname, sheet_name=0)
syndic = dict(zip(sd_df['searchTerm'],sd_df['Keyword']))


concept_df = pd.read_excel(termdictname, sheet_name=1)
concept_dict = dict(zip(concept_df['keyword'],concept_df['concept']))
sentiment_dict = dict(zip(concept_df['keyword'],concept_df['sentiment']))

#%%

# Define blacklist keywords if applicable
blacklist = []
whitelist = []

df['keywords'] = ''  # make blank column because no keywords from goodreads

# add keywords from text: find search terms and map to common keyword term
# returns a series with lists of keywords, adds columns to df with 'enhanced_keywords' found in text
print("add keywords")
kwAttr = buildKeywords(df, blacklist, whitelist,
                       kwAttr='keywords', txtAttr='text',
                       syndic=syndic, addFromText=True, enhance=False)

print("keywords added")

#%%  clean keyword file  
# remove records where there was no keyword match
df = df[df['enhanced_keywords'] != ''] 
df.reset_index(inplace=True, drop=True)
# clean cols for rendering in mappr
df['label'] = df['title'] # auto node label
df['keyword list'] = df['enhanced_keywords'].str.replace("|", ", ")  # string of keywords for display
df['keywords'] = df['enhanced_keywords']
df['n_keywords'] = df['keywords'].apply(lambda x: len(x.split('|')))
df.drop(['enhanced_keywords'], axis=1, inplace=True)



#%%  Add Concept Tags
def addConcepts(kwds):
    concepts = set()
    kwdlist = set(kwds.split('|'))
    for kwd in kwdlist:
        concepts.add(concept_dict.get(kwd))
    return list(concepts)

df['concepts'] = df['keywords'].apply(lambda x: addConcepts(x))

#%%  build networks linked by KEYWORD similarity
# with IDF - downweight common terms
buildTagNetwork(df, color_attr="Cluster", tagAttr='eKwds', dropCols=[], 
                outname=kwdname_IDF,idf=True,
                nodesname=None, edgesname=None, plotfile=None,
                toFile=True, doLayout=False, draw=False)

#%%  build networks linked by KEYWORD similarity
# no IDF - do not downweight common terms
buildTagNetwork(df, color_attr="Cluster", tagAttr='eKwds', dropCols=[], 
                outname=kwdname_noIDF,idf=False,
                nodesname=None, edgesname=None, plotfile=None,
                toFile=True, doLayout=False, draw=False)

#%%  build networks linked by CONCEPT similarity
# with IDF - downweight common terms
buildTagNetwork(df, color_attr="Cluster", tagAttr='concepts', dropCols=[], 
                outname=cncptname_IDF,idf=True,
                nodesname=None, edgesname=None, plotfile=None,
                toFile=True, doLayout=False, draw=False)

#%%  build networks linked by CONCEPT similarity
# NO IDF - downweight common terms
buildTagNetwork(df, color_attr="Cluster", tagAttr='concepts', dropCols=[], 
                outname=cncptname_noIDF,idf=False,
                nodesname=None, edgesname=None, plotfile=None,
                toFile=True, doLayout=False, draw=False)



#%%  #### load and clean network files ### remove large text block
# TODO: return df from build network (instead of exporting and importing file)

def cleanNetwork(netdf, netfile):    
    dropCols = ['text', 'eKwds', 'year_20-21st-Century',]
    ndf = netdf.parse('Nodes')
    ldf = netdf.parse('Links')
    ndf.drop(dropCols, axis=1, inplace=True)
    ndf['concepts'] = df['concepts'].apply(lambda x: '|'.join(x)) #convert list to string


    #write ouit network file excel file with 2 sheets
    writer = pd.ExcelWriter(netfile)
    ndf.to_excel(writer,'Nodes', index=False)
    ldf.to_excel(writer,'Links', index=False)
    writer.save() 
    print('writing network excel files')
    return ndf

print('cleaning network files')

# clean keyword Network IDF file
kwd_netdfIDF = pd.ExcelFile(kwdname_IDF) # read network xlsx with nodes and links sheets
ndfIDF = cleanNetwork(kwd_netdfIDF, kwdname_IDF) # clean and rewrite xlsx file w 2 sheets 

# clean keyword Network noIDF file
kwd_netdfNoIDF = pd.ExcelFile(kwdname_noIDF) # read network xlsx with nodes and links sheets
ndfNoIDF = cleanNetwork(kwd_netdfNoIDF, kwdname_noIDF) # clean and rewrite xlsx file w 2 sheets 

# clean concept Network IDF file
cncpt_netdfIDF = pd.ExcelFile(cncptname_IDF) # read network xlsx with nodes and links sheets
cncpt_ndfIDF = cleanNetwork(cncpt_netdfIDF, cncptname_IDF) # clean and rewrite xlsx file w 2 sheets 

# clean concept Network noIDF file
cncpt_netdfNoIDF = pd.ExcelFile(cncptname_noIDF) # read network xlsx with nodes and links sheets
cncpt_ndfNoIDF = cleanNetwork(cncpt_netdfNoIDF, cncptname_noIDF) # clean and rewrite xlsx file w 2 sheets 



