#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 10:58:06 2017

@author: eric.berlow
"""

import os.path
import pandas as pd
import glob as glob
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

datapath = "GR_Reviews"
outpath = "Results"
outname = "scifi.txt"

# read in list of files (pathnames) from folder
print("reading files from %s"%datapath)
all_files = glob.glob(os.path.join(datapath, "*.tsv")) # get list of filenames from directory
df_all_files = (pd.read_csv(f, sep='\t') for f in all_files) #read in list of files
df = pd.concat(df_all_files, ignore_index=True)  # concatenated dataframe of all files in list
df = df.dropna(subset=['Reviews']) # remove records with no reviews
df = df.fillna('')
df['Reviews'] = df['Reviews'].str.lower()
df.rename(columns={'Reviews': 'text'}, inplace=True)
df['keywords'] = ''

#df = df.iloc[0:500,:] #test with first 500 records

# write tab-delmited text file
print("writing output file to %s"%outpath)
df.to_csv(os.path.join(outpath, outname), sep='\t', header=True, index=False)



