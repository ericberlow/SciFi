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
sdname = os.path.join(dictpath, "scifi_syndic_conceptdic.xlsx")
fname = os.path.join(datapath, "scifi_201807.txt") 
outname_noIDF = os.path.join(datapath, "scifi_network_noIDF_201807.xlsx")
outname_IDF = os.path.join(datapath, "scifi_network_IDF_201807.xlsx")

#plotfile = os.path.join(datapath, "scifi_plot_IDF_4-4-18.pdf")

#%%

# read text and keyword file
print ('reading text file')
df = pd.read_csv(fname, sep='\t', header=0, encoding='utf-8')
print ('data reading done')
df = df.fillna('')
df['year'] = df['year'].apply(pd.to_numeric) 
df = df[df['year']>=1850] # keep all books published since 1900
#df = df.iloc[0:500,:] #test with first 500 records
#%%

# read dictonary of search terms mapped to common terms (key is search term, value is unique common term)
sd_df = pd.read_excel(sdname)
syndic = dict(zip(sd_df['Search Term'],sd_df['Keyword']))
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

#%%   
# remove records where there was no keyword match
df = df[df['enhanced_keywords'] != ''] 
df.reset_index(inplace=True, drop=True)
# clean cols for rendering in mappr
df['label'] = df['title'] # auto node label
df['keyword list'] = df['enhanced_keywords'].str.replace("|", ", ")  # string of keywords for display
df['keywords'] = df['enhanced_keywords'] 
df.drop('enhanced_keywords', axis=1, inplace=True)


totBooks = len(df)

#%%

# build networks linked by keyword similarity
# do not downweight common terms (No IDF)
buildTagNetwork(df, color_attr="Cluster", tagAttr='eKwds', dropCols=[], 
                outname=outname_noIDF,idf=False,
                nodesname=None, edgesname=None, plotfile=None,
                toFile=True, doLayout=False, draw=False)
#%%

# downweight common terms (with IDF)
buildTagNetwork(df, color_attr="Cluster", tagAttr='eKwds', dropCols=[], 
                outname=outname_IDF,idf=True,
                nodesname=None, edgesname=None, plotfile=None,
                toFile=True, doLayout=False, draw=False)

#%%  #### load and clean network files 
# TODO: return df from build network (instead of exporting and importing file)

def cleanNetwork(netdf, netfile):    
    dropCols = ['text', 'eKwds', 'year_20-21st-Century',]
    ndf = netdf.parse('Nodes')
    ldf = netdf.parse('Links')
    ndf.drop(dropCols, axis=1, inplace=True)

    #write ouit network file excel file with 2 sheets
    writer = pd.ExcelWriter(netfile)
    ndf.to_excel(writer,'Nodes', index=False)
    ldf.to_excel(writer,'Links', index=False)
    writer.save() 
    return ndf

# clean IDF file
IDFname = "Results/scifi_network_IDF_201807.xlsx"
netdfIDF = pd.ExcelFile(IDFname) # read network xlsx with nodes and links sheets
ndfIDF = cleanNetwork(netdfIDF, IDFname) # clean and rewrite xlsx file w 2 sheets 

# clean noIDF file
noIDFname = "Results/scifi_network_noIDF_201807.xlsx"
netdfNoIDF = pd.ExcelFile(noIDFname) # read network xlsx with nodes and links sheets
ndfNoIDF = cleanNetwork(netdfNoIDF, noIDFname) # clean and rewrite xlsx file w 2 sheets 





#%%   #################### 

# function to create df with tag counts and percents sorted by most common for histogram, 
def buildTagHistDf (df, col):
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
## create and save, display tag histogram ##

## build df for tag histograms
tags_df = buildTagHistDf(df, 'keywords') 

print('make, display, save tag histogram')

tagBars = hv.Bars(tags_df,'keywords', 'count').options(
        color=hv.Cycle(values=Colors), color_index='keywords', 
        invert_axes=True, invert_yaxis=True,
        width=1200, height=800, tools=['hover'], yaxis='bare',
        show_legend=False, show_grid=True ) 

# Convert to bokeh plot then save and show using bokeh
reset_output() # clear output_file
renderer = hv.renderer('bokeh')
tagPlot = renderer.get_plot(tagBars).state
output_file("tagHist.html") #name of file to launch in browser
show(tagPlot)
  
    
#%%  ####################################
## create and save, display cluster histograms for each run ##

print('make dataframe of tag for each network run')
clusIDF = ndfIDF['cluster_name'].str.strip()
clusNoIDF = ndfNoIDF['cluster_name'].str.strip()
clusdf = pd.DataFrame({'cluster_IDF': clusIDF, 'cluster_noIDF':clusNoIDF})
clusdf = clusdf.fillna('')


print('make, display, save keyword cluster histograms for IDF vs noIDF')

IDFclusters = buildTagHistDf(clusdf, 'cluster_IDF')
noIDFclusters = buildTagHistDf(clusdf, 'cluster_noIDF')

clusIDF_Bars = hv.Bars(IDFclusters,'cluster_IDF', 'count' ).options(
        color=hv.Cycle(values=Colors), color_index='cluster_IDF',
        width=750, height=600,
        invert_axes=True,invert_yaxis=True, tools=['hover'], yaxis='bare',
        show_legend=False, show_grid=True )

clusNoIDF_Bars = hv.Bars(noIDFclusters,'cluster_noIDF', 'count' ).options(
        color=hv.Cycle(values=Colors), color_index='cluster_noIDF',
        width=600, height=600,
        invert_axes=True,invert_yaxis=True, tools=['hover'], yaxis='bare',
        show_legend=False, show_grid=True )

clusLayout = hv.Layout(clusIDF_Bars + clusNoIDF_Bars).cols(2)

# Convert to bokeh plot then save and show using bokeh
reset_output() # clear output_file
clusPlot = renderer.get_plot(clusLayout).state
output_file("clusHist.html") #name of file to launch in browser
show(clusPlot)








