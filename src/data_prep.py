import os
import glob
import boto3
import pandas as pd
import numpy as np
import psycopg2
import sqlalchemy as sa
from sqlalchemy import text
import time
from sklearn.model_selection import train_test_split
import math
import re
from pathlib import Path
import datetime


#Create pivot tables
def pivot_index(df, columns, target_var = '', target_types = ''):
    """
    Desc: Takes a raw dataframe and produces a single dataframe object with multiple main dataframes
    
    Params:
        df: raw dataframe
        columns: list of categorical columns, note this should be specified seperately from the df object
        target_var: name of the target variable (default allows regular histogram tables to be generated)
        target_types: the names of the two target values (default allows regular histogram tables to be generated)
             
        
    output: 
        pivots: the collection of pivots generated from df 
    
    """
    if target_var == '':
        
        pivots = {c: pd.DataFrame() for c in columns}
        for col in columns:
            #print(col) # debug tool
            temp = df.groupby([col]).size().fillna(0).to_frame(name='vals')
            pivots[col] = temp
    
    
    else:
    
        pivots = {c: pd.DataFrame() for c in columns}
        for col in columns:
            #print(col) # debug tool
            temp = df.groupby([col, target_var]).size().unstack().fillna(0)
            temp.columns = target_types
            pivots[col] = temp
    
    return pivots

def date_detect(df):
    """
    COULD BE OPTIMISED BY NOT LOOKING FOR MAX
    Desc: finds columns likely to be dates in a dataframe
    
    Params:
        dt: input dataframe
        
    output: 
        date_list: returns names of columns in dt likely to be in date format
    
    """

    test = df.select_dtypes(include=['object'])
    date_list = list(df.select_dtypes(include=['datetime']).columns)
    
    for col in test.columns:
        try:
            df[col] = pd.to_datetime(df[col])
            date_list.append(col)
        except:
            pass
    return date_list

class Data_Prep: # this takes a while, could make the df objects a bit more efficient by fixing how they are used in the config and graph generating steps

    def __init__(self, df, target_var = '', id_threshold = 0.5, null_threshold = 0.99):
        
        self.df = df
        self.target_var = target_var
        
        self.Ids_cats = [col for col in df.columns if len(df[col].unique())/(len(df[col].dropna())+1) >= id_threshold]
        print("detected " + str(len(self.Ids_cats)) + " ID variables:")
        print(self.Ids_cats)
        
        # flags/trivial variables
        self.trivial = [col for col in df.columns if len(df[col].dropna().value_counts()) == 1]
        print("detected " + str(len(self.trivial)) + " trivial variables (only one unique value):")
        print(self.trivial)
        
        #likely date columns
        self.date_cols = date_detect(df)
        print("detected " + str(len(self.date_cols)) + " date variables:")
        print(self.date_cols)
        
        #empty variables exclusion list
        self.null_cols = [col for col in df.columns if len(df[col].dropna())/len(df) <= (1 - null_threshold) ]
        print("detected " + str(len(self.null_cols)) + " heavy null variables:")
        print(self.null_cols)
        
        # Excludes analysing numerical columns that are completely missing in one of the target classes
        try:
            self.num_exclude = [col for col in df.select_dtypes(include=['float64', 'int64']).columns if len(df.groupby([col, target_var]).size().unstack().fillna(0).columns) < 2]
        except KeyError:
            self.num_exclude =[]
        print("detected " + str(len(self.num_exclude)) + " variables which are missing in a level of the class:")
        print(self.num_exclude)
        

        self.total_exclude = self.Ids_cats + self.trivial + self.date_cols + self.null_cols + self.num_exclude
        
        
        #Sets up Column Lists sorted by categorical/numeric, while excluding columns listed in Section

        # set up subsets
        self.df_numeric = df[[col for col in df.columns if col != target_var and col not in self.total_exclude]].select_dtypes(include=['float64', 'int64']).copy()
        self.df_cat = df[[col for col in df.columns if col != target_var and col not in self.total_exclude]].select_dtypes(include=['object']).copy()

        self.numeric_cols = self.df_numeric.columns
        self.cat_cols = self.df_cat.columns
        
        # adding target to front of each subset
        try:
            self.df_numeric.insert(loc = 0, column = self.target_var, value = self.df[[self.target_var]])
            self.df_cat.insert(loc = 0, column = self.target_var, value = self.df[[self.target_var]])
        except KeyError:
            print("Histograms Only")
    
    def define_target(self):
        target_vals = list(self.df[self.target_var].unique())
        print(target_vals)

        if len(target_vals) > 2:
            print('input desired target class') 
            desired_target = str(input())

            self.df[self.target_var] = ['target' if i == desired_target else 'non_target' for i in self.df[self.target_var] ]
            self.df_numeric[self.target_var] = self.df[self.target_var]
            self.df_cat[self.target_var] = self.df[self.target_var]
            
            self.multiclass_ind = 1 #functionality to be added using this indicator

        else:
            self.multiclass_ind = 0
            print('not multiclass')
            
    def label_target(self):
        # enter names for what your targets mean. do based on the order shown by the previous cell
        target_vals = list(self.df[self.target_var].unique())
        print(target_vals)
        
        if self.target_var != '':
            self.target_types = []
            print("input label for first shown target class e.g. non-churn")
            self.target_types.append(str(input()))
            print("input label for second shown target class e.g. churn vol")
            self.target_types.append(str(input()))
        else: 
            print("Histograms Only")

