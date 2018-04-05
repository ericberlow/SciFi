#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 10:58:06 2017

@author: eric.berlow
"""

import os.path
import pandas as pd
import json
import glob as glob
import sys
import numpy as np

reload(sys)
sys.setdefaultencoding('utf-8')

datapath = "data_json"
outpath = "Results"
outname = "scifi_4-2-18.txt"


def getYearFn (x):
    strings = x.split("(")
    if len(strings) == 2: #if paren, there are 2 yrs - original is last word in parentheses
        yr = strings[1].split(' ')[-1].replace(')','') #get second string, split words, take last one, remove paren
    elif len(strings) == 1:
        yr = strings[0].split('th ')[2] #if no parenthesis, year is 3rd word of string
    return yr
        

# read in list of files (pathnames) from folder
print("reading files from %s"%datapath)
all_files = glob.glob(os.path.join(datapath, "*.json")) # get list of filenames from directory


allbooks=[]  #book
for f in all_files:  # f is path + filename
    with open(f) as fp:
        booklist = json.load(fp)  # booklist is a list of book dictionaries from one json file 
        allbooks.extend(booklist)  # allbooks is list of all book dictionaries


# allbooks is a list of dictionaries - each main key is a book title and the value is a dictionary of data
# - we need to add the book title to the data dictionary
# for each book, get the key (i.e., title) and create a dictionary of 'title': book title 
newdata = [(v.update({'title':k}),v)[1] for book in allbooks for k,v in book.iteritems() ]

# now the data is a list of dictionaries, which can be read into dataframe
df = pd.DataFrame(newdata)

# 
'''
# 'reviews' is a nested dictionary - get the number of reviews from it
df['n_reviews'] = df['reviews'].apply(lambda x: int(x['number']))
# within reviews get the 'list of reviews' 
df['list_of_reviews'] = df['reviews'].apply(lambda x: x['list_of_reviews'])
# conctentate the list of reviews - note turned that list into a set to remove duplicate reviews
df['review_text'] = df['list_of_reviews'].apply(lambda x: ' '.join(set(x)))
# extract year from 'published' string THIS NEEDS WORK
df['year_published'] = df['published'].apply(lambda x: getYearFn(x))
df['genres_list'] = df['genres'].apply(lambda x: x['names'])
df['log_n_reviews'] = df['n_reviews'].apply(lambda x: np.round(np.log10(x+1),2))
df['genre_tags'] = df['genres_list'].apply(lambda x: '|'.join(x))
df['text'] = df['plot'] + " " + df['review_text']
dropCols = ['reviews', 'list_of_reviews', 'review_text','genres','ratings', 'published']
df.drop(dropCols, axis=1, inplace=True)

colOrder = ['title', 'genres_list','genre_tags','author','year_published',
            'log_n_reviews','n_reviews', 'plot', 'url','text']

df = df[colOrder]

'''

'''
# write tab-delmited text file
print("writing output file to %s"%outpath)
df.to_csv(os.path.join(outpath, outname), sep='\t', header=True, index=False)
#df.to_csv(os.path.join(testpath, outname), sep='\t', header=True, index=False)

'''

