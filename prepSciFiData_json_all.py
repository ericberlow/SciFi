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
        string2 = strings[0].split('th ') # [2] #if no parenthesis check that day of month is mentioned (e.g. 24th)
        if len(string2) >1:  # if split on day of month mentioned
            yr = string2[1][0:4] # year is first 4 characters after day of month
        elif len(string2) == 1:
            yr = '' #string2.split(' ')[1] # if day of month not mentioned, split on space and year is second element
    else:
        yr = ''
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
df = df.dropna(subset=['reviews']) # remove records with no reviews
df = df.fillna('')

# year is buried in a string which is not consistent
df['year_published'] = df['published'].apply(lambda x: getYearFn(x)) # STILL MISSING MANY CASES
df['n_reviews'] = df['reviews'].apply(lambda x: int(x['number'])) # within 'reviews' nested dictionary get the n review
df['log_n_reviews'] = df['n_reviews'].apply(lambda x: np.round(np.log10(x+1),2))
df['list_of_reviews'] = df['reviews'].apply(lambda x: x['list_of_reviews'])# within reviews dict get the 'list of reviews' 

# conctentate the list of reviews - note turned that list into a set to remove duplicate reviews
df['review_text'] = df['list_of_reviews'].apply(lambda x: ' '.join(set(x)))
df['text'] = df['plot'] + " " + df['review_text']

df['genres_list'] = df['genres'].apply(lambda x: x.get('names')).str.replace('None',' ' )
df['genres_list'] = df['genres_list'].apply(lambda x: list(x) if isinstance(x, basestring) else x)  # get returns 'None' if no key (missing genre list)
df['genre_tags'] = df['genres_list'].apply(lambda x: '|'.join(x))  

dropCols = ['reviews', 'list_of_reviews', 'review_text','ratings']
df.drop(dropCols, axis=1, inplace=True)

colOrder = ['title', 'genres_list','author','year_published','published',
            'log_n_reviews','n_reviews', 'plot', 'url','text', 'genres']

df = df[colOrder]


'''
# write tab-delmited text file
print("writing output file to %s"%outpath)
df.to_csv(os.path.join(outpath, outname), sep='\t', header=True, index=False)
#df.to_csv(os.path.join(testpath, outname), sep='\t', header=True, index=False)

'''

