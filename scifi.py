#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 09:01:15 2017

@author: ericlberlow
"""

# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("../Tag2Network/tag2network")

import os.path
import pandas as pd
from Tags.BuildKeywords import buildKeywords
from Network.BuildNetwork import buildTagNetwork


# Define input and output file paths
dictpath = "."
datapath = "Results"
#fname = os.path.join(datapath, "scifi_test.txt") #test with first 500 records
fname = os.path.join(datapath, "scifi.txt") 
sdname = os.path.join(dictpath, "scifi_syndic.xlsx")
outname = os.path.join(datapath, "scifi_network_noIDF.xlsx")
plotfile = os.path.join(datapath, "scifi_plot.pdf")


# read text and keyword file
print ('reading text file')
df = pd.read_csv(fname, sep='\t', header=0, encoding='utf-8')
print ('data reading done')
df = df.fillna('')
#df = df.iloc[0:500,:] #test with first 500 records

# read dictonary of search terms mapped to common terms (key is search term, value is unique common term)
sd_df = pd.read_excel(sdname)
syndic = dict(zip(sd_df.Synonym,sd_df.Keyword))

# Define blacklist keywords if applicable
blacklist = []
whitelist = []

# add keywords from text: find search terms and map to common keyword term
# enhance by splitting multi-word keywords and matching to bigrams in keyword list
print("add and enhance keywords")
kwAttr = buildKeywords(df, blacklist, whitelist,
                       kwAttr='keywords', txtAttr='text',
                       syndic=syndic, addFromText=True, enhance=True)


#list cols to remove from final file
dropCols = ['text', 'keywords'] # some books have very long comment text

# remove records where there was no keyword match
df = df[df['enhanced_keywords'] != ''] 

df['label'] = df['Title']
df['keyword list'] = df['enhanced_keywords'].str.replace("|", ", ")

# build network linked by keyword similarity
buildTagNetwork(df, color_attr="Cluster", tagAttr=kwAttr, dropCols=dropCols, 
                outname=outname,idf=False,
                nodesname=None, edgesname=None, plotfile=plotfile,
                toFile=True, doLayout=True, draw=True)



