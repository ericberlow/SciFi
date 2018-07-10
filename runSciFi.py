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




#%%   #######   PLOTS   ############# 
# TODO: move all plotting to separate script

#%%   #################### 

# function to create df with tag counts and percents sorted by most common for histogram, 
def buildTagHistDf (df, col):
    totBooks = len(df)
    tagDict = {}
    tagLists = df[col].str.split('|')
    tagLists = tagLists.apply(lambda x: [tag.strip(' ') for tag in x]) # strip empty spaces for each item in each list
    tagHist = OrderedDict(Counter([t for tags in tagLists for t in tags if t is not '']).most_common()) #excludes rows with no data
    tagDict[col] = list(tagHist.keys())
    tagDict['count'] = list(tagHist.values())
    tagdf = pd.DataFrame(tagDict)
    tagdf['pct'] = tagdf['count'].apply(lambda x: np.round((100*(x/totBooks)),2))
    return tagdf


#%%   
## create files for keyword distribution, concepts distribution, n_keywordsPerBooK counts ##
print('make dataframs of keyword distribution, concepts distribution, n keywords per book counts')

## keywords 
tags_df = buildTagHistDf(df, 'keywords') 
## concepts 
df['concepts'] = df['concepts'].apply(lambda x: '|'.join(x)) #convert list to string
concepts_df = buildTagHistDf(df, 'concepts') 

# n keywords per book count
vals, counts = np.unique(df['n_keywords'], return_counts=True)
tagcounts = pd.DataFrame({'n_keywordsPerBook':vals, 'count':counts})
tagcounts['pct'] = tagcounts['count']/tagcounts['count'].sum()

  
#%%  create, save, display histograms for keywords, clusters, and keywordsPerBook

print('make, display, save keyword and concept histograms')

kwdBars = hv.Bars(tags_df,'keywords', 'count').options(title_format='Keywords',labelled=['y'],
        color=hv.Cycle(values=Colors), color_index='keywords', 
        #invert_axes=True, invert_yaxis=True,
        width=1200, height=400, tools=['hover'], xrotation=60,
        show_legend=False, show_grid=True ) 

conceptBars = hv.Bars(concepts_df,'concepts', 'count').options(title_format='Concepts',labelled=['y'],
        color=hv.Cycle(values=Colors), color_index='concepts', 
        #invert_axes=True, invert_yaxis=True,
        width=1200, height=300, tools=['hover'], yaxis='bare', xrotation=60,
        show_legend=False, show_grid=True ) 

kwdCounts = hv.Bars(tagcounts,'n_keywordsPerBook', 'count').options(title_format='Keywords per Book',labelled=['y'],
        width=1200, height=300, tools=['hover'], yaxis='bare',
        show_legend=False, show_grid=True ) 

kwdsLayout = hv.Layout(kwdBars + conceptBars + kwdCounts).cols(1)

# Convert to bokeh plot then save and show using bokeh
reset_output() # clear output_file
renderer = hv.renderer('bokeh')
tagPlot = renderer.get_plot(kwdsLayout).state
output_file("tagHist.html") #name of file to launch in browser
show(tagPlot)


#%%  ####################################
## create dataframe of all clusters for each network ##

print('make dataframe of all culsters for each network')
kwdclusIDF = ndfIDF['cluster_name'].str.strip()
kwdclusNoIDF = ndfNoIDF['cluster_name'].str.strip()
cncpt_clusIDF = cncpt_ndfIDF['cluster_name'].str.strip()
cncpt_clusNoIDF = cncpt_ndfNoIDF['cluster_name'].str.strip()


clusdf = pd.DataFrame({'keywordCluster_IDF': kwdclusIDF, 'keywordCluster_noIDF':kwdclusNoIDF,
                       'conceptCluster_IDF': cncpt_clusIDF, 'conceptCluster_noIDF':cncpt_clusNoIDF,})
clusdf = clusdf.fillna('')

#%%  ####################################
## create and save, display cluster histograms for each run ##

print('make, display, save keyword and concept cluster histograms for IDF vs noIDF')

IDF_kwdclusters = buildTagHistDf(clusdf, 'keywordCluster_IDF')
noIDF_kwdclusters = buildTagHistDf(clusdf, 'keywordCluster_noIDF')
IDF_cncptclusters = buildTagHistDf(clusdf, 'conceptCluster_IDF')
noIDF_cncptclusters = buildTagHistDf(clusdf, 'conceptCluster_noIDF')


kwdclusIDF_Bars = hv.Bars(IDF_kwdclusters,'keywordCluster_IDF', 'count' ).options(title_format='Keyword Clusters  IDF',labelled=['x'],
        color=hv.Cycle(values=Colors), color_index='keywordCluster_IDF', width=750, height=600,
        invert_axes=True,invert_yaxis=True, tools=['hover'], show_legend=False, show_grid=True )

kwdclusNoIDF_Bars = hv.Bars(noIDF_kwdclusters,'keywordCluster_noIDF', 'count' ).options(title_format='Keyword Clusters noIDF',labelled=['x'],
        color=hv.Cycle(values=Colors), color_index='keywordCluster_noIDF', width=650, height=600,
        invert_axes=True,invert_yaxis=True, tools=['hover'], show_legend=False, show_grid=True )

cncptclusIDF_Bars = hv.Bars(IDF_cncptclusters,'conceptCluster_IDF', 'count' ).options(title_format='Concept Clusters IDF',labelled=['x'],
        color=hv.Cycle(values=Colors), color_index='conceptCluster_IDF', width=750, height=600,
        invert_axes=True,invert_yaxis=True, tools=['hover'], show_legend=False, show_grid=True )

cncptclusNoIDF_Bars = hv.Bars(noIDF_cncptclusters,'conceptCluster_noIDF', 'count' ).options(title_format='Concept Clusters noIDF',labelled=['x'],
        color=hv.Cycle(values=Colors), color_index='conceptCluster_noIDF', width=650, height=600,
        invert_axes=True,invert_yaxis=True, tools=['hover'], show_legend=False, show_grid=True )


clusLayout = hv.Layout(kwdclusIDF_Bars + kwdclusNoIDF_Bars + cncptclusIDF_Bars + cncptclusNoIDF_Bars).cols(2)

# Convert to bokeh plot then save and show using bokeh
reset_output() # clear output_file
clusPlot = renderer.get_plot(clusLayout).state
output_file("clusHist.html") #name of file to launch in browser
show(clusPlot)



