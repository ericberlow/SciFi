#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 10:54:17 2018

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
kwdname_IDF = os.path.join(datapath, "scifi_network_IDF_201807.xlsx")
kwdname_noIDF = os.path.join(datapath, "scifi_network_noIDF_201807.xlsx")
cncptname_IDF = os.path.join(datapath, "scifi_conceptNetwork_IDF_201807.xlsx")
cncptname_noIDF = os.path.join(datapath, "scifi_conceptNetwork_noIDF_201807.xlsx")


#%%   #################### 
print('reading nodes files')

ndfIDF = pd.read_excel(kwdname_IDF, sheet_name='Nodes') # read nodes file
ndfNoIDF = pd.read_excel(kwdname_noIDF, sheet_name='Nodes') # read nodes file
cncpt_ndfIDF = pd.read_excel(cncptname_IDF, sheet_name='Nodes') # read nodes file
cncpt_ndfNoIDF = pd.read_excel(cncptname_noIDF, sheet_name='Nodes') # read nodes file



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
tags_df = buildTagHistDf(ndfIDF, 'keywords') 
## concepts 
concepts_df = buildTagHistDf(ndfIDF, 'concepts') 

# n keywords per book count
vals, counts = np.unique(ndfIDF['n_keywords'], return_counts=True)
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

kwdsLayout = hv.Layout(kwdBars + conceptBars + kwdCounts).cols(1).options(
        sizing_mode='scale_width', normalize=False, shared_axes=False)

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


clusLayout = hv.Layout(kwdclusIDF_Bars + kwdclusNoIDF_Bars + cncptclusIDF_Bars + cncptclusNoIDF_Bars).cols(2).options(
        sizing_mode='scale_width', normalize=False, shared_axes=False)

# Convert to bokeh plot then save and show using bokeh
reset_output() # clear output_file
clusPlot = renderer.get_plot(clusLayout).state
output_file("clusHist.html") #name of file to launch in browser
show(clusPlot)



