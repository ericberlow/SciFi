#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 06:50:15 2018

@author: ericlberlow
"""
#%%
### What this script does
## generates an file used for annotating the AI trends over time with  the major time periods in the history of AI
## The source for defining time periods in AI history was https://en.wikipedia.org/wiki/History_of_artificial_intelligence 
## output file is AI_time_periods.xlsx 


#%% #############
#  ADD CHART ANNOTATIONS FOR TIME PERIODS

import pandas as pd


#%% #############
#  ADD CHART ANNOTATIONS FOR TIME PERIODS

## Birth of AI 1952-1956 ##
birth_x = list(range(1952, 1957))  
birth_y = [1.5]*len(birth_x)
birth_label = ["1952-56: Birth of AI"]*len(birth_x)
birth_yrs = ["1952-1956"]*len(birth_x)
birth_period = ["Birth of AI"]*len(birth_x)
birth_df = pd.DataFrame({'year':birth_x, 'y': birth_y, 'time_period': birth_label,
                         'years': birth_yrs, 'period': birth_period})

## Golden Years 1956-1973 ##
golden_x = list(range(1956, 1974))  
golden_y = [1.6]*len(golden_x)
golden_label = ["1956-73: Golden Years"]*len(golden_x)
golden_yrs = ["1956-1973"]*len(golden_x)
golden_period = ["Golden Years"]*len(golden_x)
golden_df = pd.DataFrame({'year':golden_x, 'y': golden_y, 'time_period': golden_label,
                         'years': golden_yrs, 'period': golden_period})

## First AI Winter 1973-1980 ##
winter1_x = list(range(1973,1981))
winter1_y = [1.5]*len(winter1_x)
winter1_label = ["1973-80: 1st AI Winter"]*len(winter1_x)
winter1_yrs = ["1973-1980"]*len(winter1_x)
winter1_period = ["1st AI Winter"]*len(winter1_x) 
winter1_df = pd.DataFrame({'year':winter1_x, 'y': winter1_y, 'time_period': winter1_label,
                           'years': winter1_yrs, 'period': winter1_period})

## Expert System Boom  1980 - 1987 ##
boom_x = list(range(1980, 1988))
boom_y = [1.6]*len(boom_x)
boom_label = ["1980-87: Expert Systems"]*len(boom_x)
boom_yrs = ["1980-1987"]*len(boom_x)
boom_period = ["Expert Systems"]*len(boom_x) 
boom_df = pd.DataFrame({'year':boom_x, 'y': boom_y,  'time_period': boom_label,
                        'years': boom_yrs, 'period': boom_period})

## Second AI Winter 1987 - 1993 ##
winter2_x = list(range(1987,1994))
winter2_y = [1.5]*len(winter2_x)
winter2_label = ["1987-93: 2nd AI Winter"]*len(winter2_x)
winter2_yrs = ["1987-1993"]*len(winter2_x)
winter2_period = ["2nd AI Winter"]*len(winter2_x) 

winter2_df = pd.DataFrame({'year':winter2_x, 'y': winter2_y, 'time_period': winter2_label,
                           'years': winter2_yrs, 'period': winter2_period})


## Quiet Years - Quite Progress 1993 - 2011##
quiet_x = list(range(1993,2012))
quiet_y = [1.6]*len(quiet_x)
quiet_label = ["1993-2011: Quiet Progress"]*len(quiet_x)
quiet_yrs = ["1993-2011"]*len(quiet_x)
quiet_period = ["Quiet Progress"]*len(quiet_x) 

quiet_df = pd.DataFrame({'year':quiet_x, 'y': quiet_y, 'time_period':quiet_label,
                         'years': quiet_yrs, 'period': quiet_period})

## Big Data Bump - Deep Learning Boom 2011 - 2016##
bigdata_x = list(range(2011,2017))
bigdata_y = [1.7]*len(bigdata_x)
bigdata_label = ["2011-16: Big Data"]*len(bigdata_x)
bigdata_yrs = ["1993-2011"]*len(bigdata_x)
bigdata_period = ["Big Data Era"]*len(bigdata_x) 
bigdata_df = pd.DataFrame({'year':bigdata_x, 'y': bigdata_y, 'time_period': bigdata_label,
                           'years': bigdata_yrs, 'period': bigdata_period})

## Combine into one file of time periods.  Write out to excel
annotate_df = pd.concat([birth_df, golden_df, winter1_df, boom_df, winter2_df, quiet_df, bigdata_df], sort=False)
annotate_df.sort_values(by='year', ascending=True, inplace=True)
annotate_df.to_excel("AI_time_periods.xlsx", index=False)
