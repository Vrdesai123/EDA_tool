import time
import os
import pandas as pd
import numpy as np
import matplotlib
import seaborn as sns
import matplotlib.pyplot as plt

#Generate custom sort list function
def custom_sort(df):
    """
    Desc: 
        Prompts the user to enter the custom order they want by the index
    
    Params:
    
        df: the data which is to be sorted
        
    output: list of integers which specifies the index order
    
    """    

    
    df = df.reset_index().reset_index()
    order = []
    print("Input index order e.g: 32014")
    print(df.iloc[:,0].astype(str) + ": " + df.iloc[:,1].astype(str)) 
    for i in range(len(df)):
        while True:
            try:
                a = int(input())
            except ValueError:
                print("please input a number")
                continue
            if not 0 <= a < len(df):
                print("please input a valid number")
                continue
            else:
                break        
        order.append(a)
    return order


#long runtime means lots of cateogires: Recategorisation is necessary
def cat_graph_generate(df, target_types, config_df, root_folder, columns = []):
    """
    Desc: 
        Runs through the configuration file and treats the pivots, resulting in bar & line graphs
    
    Params:
    
        df: named dataframes which should be in pivot form already
        columns: list of categorical columns, note this should be specified seperately from the df object (categorical col list is default as per Section 4)
        target_types: the names of the two target names
        config_df: configuration dataframe 
        Root_folder: name of parent folder to save graphs
        
    output: it saves graphs to the directory
        time_list: runtime for each graph to identify pain points
    """
    if columns == []:
        columns = list(config_df.index)
    
    time_list = []
    
    for cat in columns:
        
        start = time.time()
        
        config = config_df.loc[cat]
        temp = df[cat]
        
        #Config based data adjustments
        
        if config['custom_sort'] == 1:
            
            my_file = Path(root_folder + "/Config/custom_sort/" + cat + ".csv")
            
            if my_file.is_file():
                order = pd.read_csv(root_folder + "/Config/custom_sort/" + cat + ".csv").iloc[:,0].to_list()
            else:
                order = custom_sort(temp)
                order_config = pd.DataFrame(order, columns = [cat])
                order_config.to_csv(root_folder + "/Config/custom_sort/" + cat + ".csv", index = False)
                
           
            temp = temp.reset_index()
            temp = temp.reindex(order)
            temp = temp.set_index(cat)
            
        elif config['asc/desc'] == -1: 
            
            temp = temp.sort_values([target_types[1]], ascending=False)
            
        elif config['asc/desc'] == 1:
            
            temp = temp.sort_values([target_types[1]], ascending=True) 
            
        if config['soft_cat_limit'] != 0:
            
            other = pd.DataFrame(temp.iloc[int(config['soft_cat_limit']):].sum(), columns = ['other/unsp']).transpose()
            temp = temp.iloc[:int(config['soft_cat_limit'])]
            temp = pd.concat([temp, other], ignore_index=False)
        
        if config['hard_cat_limit'] != 0:
            
            temp = temp.iloc[:config['hard_cat_limit']]
                    
        #By default divides second target_var (churn) entry type by first (non-churn)
        temp['index'] = temp[target_types[1]].transform(lambda x: x/sum(x))/temp[target_types[0]].transform(lambda x: x/sum(x))
        temp['index benchmark'] = 1
        
        #Graphing steps
        matplotlib.rc_file_defaults()
        ax1 = sns.set_style(style=None, rc=None )

        fig, ax1 = plt.subplots(figsize=(12,6))

        ax2 = ax1.twinx()

        sns.pointplot(data = temp, x = temp.index, y= 'index', ax=ax2, colour = "#22b6f5")
        sns.pointplot(data = temp, x = temp.index, y= 'index benchmark', 
                      linestyles= "--", color="#071cb5", scale = 0.5, ax=ax2)


        
        #Assumes churn is second entry in target_types list
        sns.barplot(data = temp, x = temp.index, y= target_types[1], alpha=0.5, ax=ax1, color = "#8dd3d6")


        plt.savefig(root_folder + '/Categorical/' + cat + '.jpg')
        plt.close()
        time_list.append((time.time()-start))
    return time_list #check runtime



#long runtime means lots of cateogires: Recategorisation is necessary
def cat_graph_generate_hist(df, config_df, root_folder, columns = []):
    """
    Desc: 
        Runs through the configuration file and treats the pivots, resulting in bar & line graphs
    
    Params:
    
        df: named dataframes which should be in pivot form already
        columns: list of categorical columns, note this should be specified seperately from the df object (categorical col list is default as per Section 4)
        target_types: the names of the two target names
        config_df: configuration dataframe 
        Root_folder: name of parent folder to save graphs
        
    output: it saves graphs to the directory
        time_list: runtime for each graph to identify pain points
    """
    
    if columns == []:
        columns = list(config_df.index)
    
    time_list = []
    
    for cat in columns:
        
        start = time.time()
        
        config = config_df.loc[cat]
        temp = df[cat]
        
        #Config based data adjustments
        
        if config['custom_sort'] == 1:
            
            my_file = Path(root_folder + "/Config/custom_sort/" + cat + ".csv")
            
            if my_file.is_file():
                order = pd.read_csv(root_folder + "/Config/custom_sort/" + cat + ".csv").iloc[:,0].to_list()
            else:
                order = custom_sort(temp)
                order_config = pd.DataFrame(order, columns = [cat])
                order_config.to_csv(root_folder + "/Config/custom_sort/" + cat + ".csv", index = False)
                
           
            temp = temp.reset_index()
            temp = temp.reindex(order)
            temp = temp.set_index(cat)
            
        elif config['asc/desc'] == -1: 
            
            temp = temp.sort_values(['vals'], ascending=False)
            
        elif config['asc/desc'] == 1:
            
            temp = temp.sort_values(['vals'], ascending=True) 
            
        if config['soft_cat_limit'] != 0:
            
            other = pd.DataFrame(temp.iloc[int(config['soft_cat_limit']):].sum(), columns = ['other/unsp']).transpose()
            temp = temp.iloc[:int(config['soft_cat_limit'])]
            temp = pd.concat([temp, other], ignore_index=False)
        
        if config['hard_cat_limit'] != 0:
            
            temp = temp.iloc[:config['hard_cat_limit']]
                    
 
        
        #Graphing steps
        matplotlib.rc_file_defaults()
        ax1 = sns.set_style(style=None, rc=None )

        fig, ax1 = plt.subplots(figsize=(12,6))

        
        #Assumes churn is second entry in target_types list
        sns.barplot(data = temp, x = temp.index, y= temp['vals'], alpha=0.5, ax=ax1)

        plt.savefig(root_folder + '/Categorical/' + cat + '.jpg')
        plt.close()
        time_list.append((time.time()-start))
    return time_list #check runtime



def numeric_graph_generate(df, target_types, config_df, root_folder, columns =[]):
    """
    Desc: Runs through the configuration file and treats the pivots, resulting in bar & line graphs
    
    Params:
    
        df: named dataframes which should be in pivot form already
        columns: list of numerical columns, note this should be specified seperately from the df object
        target_types: the names of the two target names
        config_df: configuration dataframe        
        root_folder: name of parent folder to save graphs
        
    output: it saves graphs to the directory
    time_list: runtime for each graph to identify pain points
    
    """
    if columns == []:
        columns = list(config_df.index)
    
    time_list = []
    
    for cat in columns:
        start = time.time()
        config = config_df.loc[cat]
        temp = df[cat]
        
        print(cat)
        #Config based data adjustments
        
        if config['bin_length'] != 0:
            temp['x']=temp.index
            temp['bins'] = pd.cut(temp.x, bins = np.arange(min(temp.x),max(temp.x),config['bin_length']).tolist())
        
        if config['upper_class'] != 0:
            
            max_class = pd.DataFrame(temp.iloc[temp.index.get_loc(config['upper_class']):].sum(), columns = [config['upper_class']]).transpose() # add < label
            temp = temp.iloc[:temp.index.get_loc(config['upper_class'])]
            temp = pd.concat([temp, max_class], ignore_index=False)
            
        if config['lower_class'] != 0:
            
            min_class = pd.DataFrame(temp.iloc[:temp.index.get_loc(config['lower_class'])].sum(), columns = [config['lower_class']]).transpose() # add < label
            temp = temp.iloc[temp.index.get_loc(config['lower_class'])+1:]
            temp = pd.concat([min_class, temp], ignore_index=False)
            
        if config['bin_length'] != 0: #reindex
            temp['x']=temp.index
            temp['bins'] = temp['bins'].fillna(temp.x).astype(str)
            
            test2 = temp[['bins', target_types[1], target_types[0]]].groupby(['bins']).sum().fillna(0)
            test2['index'] = test2[target_types[1]].transform(lambda x: x/sum(x))/test2[target_types[0]].transform(lambda x: x/sum(x))
            test2['index benchmark'] = 1
            
            l = []

            for i in test2.index:
                if '(' in i:
                    start = i.find(", ") + len(", ")
                    end = i.find("]")
                    substring = i[start:end]
                    l.append(float(substring))
                else:
                    l.append(float(i))

            test2.index = l
            test2.sort_index(ascending=True)
            
            temp = test2
            
        #By default divides second target_var (churn) entry type by first (non-churn)
        temp['index'] = temp[target_types[1]].transform(lambda x: x/sum(x))/temp[target_types[0]].transform(lambda x: x/sum(x))
        temp['index benchmark'] = 1
        
        #Graph step
        
        matplotlib.rc_file_defaults()
        ax1 = sns.set_style(style=None, rc=None )

        fig, ax1 = plt.subplots(figsize=(20,6))

        ax2 = ax1.twinx()

        sns.pointplot(data = temp, x = temp.index, y= 'index', ax=ax2, colour = "#22b6f5")
        sns.pointplot(data = temp, x = temp.index, y= 'index benchmark', 
                      linestyles= "--", color="#071cb5", scale = 0.5, ax=ax2)


        
        #Assumes churn is second entry in target_types list
        sns.barplot(data = temp, x = temp.index, y= target_types[1], alpha=0.5, ax=ax1, color = "#8dd3d6")


        plt.savefig(root_folder + '/Numeric/' + cat + '.jpg')
        plt.close()
        time_list.append((time.time()-start))
    return time_list  #check runtime


def numeric_graph_generate_hist(df, config_df, root_folder, columns = []):
    """
    Desc: Runs through the configuration file and treats the pivots, resulting in bar & line graphs
    
    Params:
    
        df: named dataframes which should be in pivot form already
        columns: list of numerical columns, note this should be specified seperately from the df object
        target_types: the names of the two target names
        config_df: configuration dataframe        
        root_folder: name of parent folder to save graphs
        
    output: it saves graphs to the directory
    time_list: runtime for each graph to identify pain points
    
    """
    if columns == []:
        columns = list(config_df.index)
    
    time_list = []
    
    for cat in columns:
        start = time.time()
        config = config_df.loc[cat]
        temp = df[cat]
        
        print(cat)
        #Config based data adjustments
        
        if config['bin_length'] != 0:
            temp['x']=temp.index
            temp['bins'] = pd.cut(temp.x, bins = np.arange(min(temp.x),max(temp.x),config['bin_length']).tolist())
        
        if config['upper_class'] != 0:
            
            max_class = pd.DataFrame(temp.iloc[temp.index.get_loc(config['upper_class']):].sum(), columns = [config['upper_class']]).transpose() # add < label
            temp = temp.iloc[:temp.index.get_loc(config['upper_class'])]
            temp = pd.concat([temp, max_class], ignore_index=False)
            
        if config['lower_class'] != 0:
            
            min_class = pd.DataFrame(temp.iloc[:temp.index.get_loc(config['lower_class'])].sum(), columns = [config['lower_class']]).transpose() # add < label
            temp = temp.iloc[temp.index.get_loc(config['lower_class'])+1:]
            temp = pd.concat([min_class, temp], ignore_index=False)
            
        if config['bin_length'] != 0: #reindex
            temp['x']=temp.index
            temp['bins'] = temp['bins'].fillna(temp.x).astype(str)
            
            test2 = temp[['bins', 'vals']].groupby(['bins']).sum().fillna(0)
 
            
            l = []

            for i in test2.index:
                if '(' in i:
                    start = i.find(", ") + len(", ")
                    end = i.find("]")
                    substring = i[start:end]
                    l.append(float(substring))
                else:
                    l.append(float(i))

            test2.index = l
            test2.sort_index(ascending=True)
            
            temp = test2
            
        
        #Graph step
        
        matplotlib.rc_file_defaults()
        ax1 = sns.set_style(style=None, rc=None )

        fig, ax1 = plt.subplots(figsize=(20,6))

        
        #Assumes churn is second entry in target_types list
        sns.barplot(data = temp, x = temp.index, y= temp['vals'], alpha=0.5, ax=ax1)

        plt.savefig(root_folder + '/Numeric/' + cat + '.jpg')
        plt.close()
        time_list.append((time.time()-start))
    return time_list  #check runtime