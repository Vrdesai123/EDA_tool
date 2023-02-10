import time
import os
import pandas as pd
import numpy as np
import math 


#repetitive check if input is a number
def int_check_input(question):
    """
    Desc: checks if input is integer and continues prompting if not
    
    Params:
        question: text string asking what input
             
        
    output: 
        c1: returns integer ouput 
    
    """
    
    while True:
        try:
            print(question)
            c1 = int(input())
        except ValueError:
            print("please input a number for: " + question)
            continue
        else:
            break
    return c1


def closest_value(input_list, input_value):
    """
    Desc: checks what the closest value is in a list to a given input
    
    Params:
        input_list: list of values to check against
        input_value: number to check closest value
        
    output: 
        arr[i]: returns closest value from input_list to input_value
    
    """
 
    arr = np.asarray(input_list)

    i = (np.abs(arr - input_value)).argmin()
 
    return arr[i]


class Categorical_Graph_Config:

# delete previous config file if you want auto-generate a new one on updated data

    def __init__(self, df, cols, root_folder, default_max_cat = 10):
        """
        Desc: 
            Loads existing category graph config or creates one based on basic rules

            The configurations available for categorical graphs are:
            custom_sort (binary variable indicating whether user wants to give a variable ordinality)
            asc/desc (trinary variable indicating if user wants graphs to sort by ascending {1}, descending {-1}, or no order {0} based on target value counts. NB: this configuration is skipped if custom_sort is enabled)
            soft_cat_limit (numerical input indicating if the user wants to display a maximum number of levels in a category, with any additional levels concatenating into an 'other' level. 
                            e.g. Input 7 will yield first 7 levels + 1 level combining all others)
            hard_cat_limit (numerical input indicating if the user wants to display a maximum number of levels in a category)

            Defaults are defined for asc/desc (descending is chosen) and soft_cat_limit (default_max_cat) if a category exceeds default_max_cat levels


        Params:
            df: dataframe to analyse and create default parameters
            Root_folder: parent directory folder (default specified from section 2)
            cols: column list to assign configs (default assigned as cat_cols var from Section 3)
            default_max_cat: when creating a new config file, provides the number for the soft_cat_limit logic

        output: 
            default_config_cat: dataframe object with configuration values for each category column

        """
        
        self.root_folder = root_folder
        
        try:
            self.default_config_cat = pd.read_csv(self.root_folder + "/Config/cat_config.csv", index_col=0)

            if len(self.default_config_cat) > len(cols):
                diff = list(set(self.default_config_cat.columns) - set(cols))
                print("Cols not found in category list: " + str(diff))
                print("revisit original dataframe to check for missing cols, otherwise delete existing config file")

            elif len(self.default_config_cat) < len(cols):    
                diff = list(set(cols) - set(self.default_config_cat.columns))
                print("New cols not in previously saved config file: " + str(diff))
                print("revisit original dataframe to check for missing cols, otherwise delete existing config file")

            
        except FileNotFoundError:

            self.default_config_cat = pd.DataFrame(np.zeros((len(cols),4)), columns = ['custom_sort','asc/desc','soft_cat_limit', 'hard_cat_limit']).set_index(cols)
            self.default_config_cat['soft_cat_limit'] = [0 if len(df[col].unique()) <= default_max_cat else default_max_cat for col in cols ] # setting default max at 10 if # of levels in category exceeds 10
            self.default_config_cat['asc/desc'] = -1 # descending is default
            
            self.default_config_cat.to_csv(self.root_folder + "/Config/cat_config.csv")
            
            print("config file not loaded. default created & saved")
            print(self.default_config_cat)
            
            
               

    # changing specific values in config file
    def change(self, cols_to_change = []):
        """
        Desc: 
            Changes config file based on list and saves config file for future runs

        Params:
            cols: list of categorical columns
            existing_config: previous config file to edit
            cols_to_change: list of columns to change in the config file (default is no changes)
            Root_folder: parent directory folder (default specified from section 2)


        output: 
            config: updated config file
            new_config: text string which if run as a code block, produces config as a dataframe

        """


        if not list(cols_to_change):
            pass
        else:
            for col in list(cols_to_change):
                print(col)

                n1 = int_check_input("custom_sort? (n:0 y:1)")

                if n1 == 1:
                    n2 = 0
                else:
                    n2 = int_check_input("asc/desc? (a:1 none:0 d:-1)")

                n3 = int_check_input("soft_cat_limit?")

                if n3 == 0:
                    n4 = int_check_input("asc/desc? (a:1 none:0 d:-1)")
                else:
                    n4 = 0

                n4 = int_check_input("hard_cat_limit")
                self.default_config_cat.loc[col] = [n1, n2, n3, n4]

        self.default_config_cat.to_csv(self.root_folder + "/Config/cat_config.csv")
        
        print(self.default_config_cat)

class Numerical_Graph_Config:        
        
    def __init__(self, df, cols, target_var, root_folder):
        """
        Desc: 
            Loads existing numerical graph config or creates one based on basic rules

            The configurations available for numerical graphs are:
            upper_class (assigns the maximum variable level to be seen {default assigned as 95th percentile of the target volume} )  
            lower_class (assigns the minimum variable level to be seen {default assigned as 5th percentile of the target volume} )   
            bin_length (if binning is desired for variable levels, a uniform bin-length can be assigned {assigns default using Freedman-Diaconis rule} )



        Params:
            df: list of values to check against
            root_folder: number to check closest value (default assigned as root_folder var from Section 2)
            cols: column list to assign configs (default assigned as numeric_cols var from Section 3)
            target_var: name of target variable (default assigned as per global variable in Section 3)

        output: 
            default_config_numeric: dataframe object with configuration values for each numerical column

        """    
        self.root_folder = root_folder
        
        try:
            self.default_config_numeric = pd.read_csv(root_folder + "/Config/num_config.csv", index_col=0)

            if len(self.default_config_numeric) > len(cols):
                diff = list(set(self.default_config_numeric.columns) - set(cols))
                print("Cols not found in category list: " + str(diff))

            elif len(self.default_config_numeric) < len(cols):    
                diff = list(set(cols) - set(self.default_config_numeric.columns))
                print("New cols not in previously saved config file: " + str(diff))

        except FileNotFoundError:
            print("config file not loaded. Creating Default File")

            if target_var != '':
                target_list = df.loc[df[target_var] == 1]
            else:
                target_list = df


            self.default_config_numeric = pd.DataFrame(np.zeros((len(cols),3)), columns = ['upper_class','lower_class','bin_length']).set_index(cols)

            print("calculating upper_class")
            self.default_config_numeric['upper_class'] = [closest_value(list(df[col].dropna().sort_values(ascending = False).unique()), target_list[col].quantile(0.95)) for col in cols]

            print("calculating lower_class")
            self.default_config_numeric['lower_class'] = [closest_value(list(df[col].dropna().sort_values(ascending = False).unique()), target_list[col].quantile(0.05)) for col in cols]

            print("calculating bin_length")
            self.default_config_numeric['bin_length'] = [math.ceil(2*(target_list[col].quantile(0.75) - target_list[col].quantile(0.25))/(len(target_list[col].dropna())**(1/3))) for col in cols]

            self.default_config_numeric.to_csv(self.root_folder + "/Config/num_config.csv")
            
            print("config file not loaded. default created & saved")
            print(self.default_config_numeric)

        


    def change(self, cols_to_change = []):
        """
        Desc: makes spot changes and saves the numerical config file

        Params:
            cols: list of numerical columns
            existing_config: previous config file to edit
            cols_to_change: list of columns to change the config file for


        output: 
            config: updated config file
            new_config: text string which if run as a code block, produces config as a dataframe

        """

        

        if not list(cols_to_change):
            pass
        else:
            for col in list(cols_to_change):
                print(col)
                n1 = int_check_input("upper_class? (n:0 y: input_value)")
                n2 = int_check_input("lower_class? (n:0 y: input_value)")
                n3 = int_check_input("bin_length?")
                self.default_config_numeric.loc[col] = [n1, n2, n3]

       
        self.default_config_numeric.to_csv(self.root_folder + "/Config/num_config.csv")
        print(self.default_config_numeric)