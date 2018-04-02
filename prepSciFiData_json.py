#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 10:58:06 2017

@author: eric.berlow
"""

import os.path
import pandas as pd
import json
#import glob as glob
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

datapath = "data_json"
outpath = "Results"
outname = "scifi_4-2-18.txt"

with open(os.path.join(datapath, "page_60.json")) as fp:
    bookdata = json.load(fp)

# bookdata is a list of books - we need to add the book title to the data dictionary
# for each book, get the key and create a dictionary of 'title': book title 
newdata = [(v.update({'title':k}),v)[1] for book in bookdata for k,v in book.iteritems() ]

# now the data is a list of dictionaries, which can be read into dataframe
df = pd.DataFrame(newdata)

# 'reviews' is a nexted dictionary - get the number of reviews from it
df['number_of_reviews'] = df['reviews'].apply(lambda x: x['number'])
# within reviews get the 'list of reviews' 
df['list_of_reviews'] = df['reviews'].apply(lambda x: x['list_of_reviews'])
# conctentate the list of reviews - note first turned that list into a set to remove duplicates
df['review_text'] = df['list_of_reviews'].apply(lambda x: ' '.join(set(x)))
# extract year from 'published' string THIS NEEDS WORK
df['year'] = df['published'].apply(lambda x: x.split(' ')[-1][:-1])

dropCols = ['reviews', 'list_of_reviews']
df.drop(dropCols, axis=1, inplace=True)


#df = pd.read_json(os.path.join(datapath, "page_60.json"), orient = 'index')

'''
# write tab-delmited text file
print("writing output file to %s"%outpath)
df.to_csv(os.path.join(outpath, outname), sep='\t', header=True, index=False)
#df.to_csv(os.path.join(testpath, outname), sep='\t', header=True, index=False)

'''

