import numpy as np
import pandas as pd

class Data:
    def __init__(self, dataset):
        
        '''loading dataframes'''
        
        self.dataset = dataset
        self.process_data()
        
    def process_data(self):
        self._create_df()
        self._column_info()
        self._print_df_stats()
        self._check_duplicates()
       
    def _create_df(self):
        '''loads and prepares dataframe'''
        self.df = self._load_dataset(dataset)        
        
    def _column_info(self):
        self.cat_cols = self._cat_cols(self.df)
        self.num_cols = self._num_cols(self.df)
        
    def _print_df_stats(self):
        print('  \n ----------Train Data Info---------')
        self.printstats(self.df)
        self._check_nan(self.df)
    
    def _load_dataset(self, file):
        return pd.read_excel(file)
    
    def printstats(self, df):
        print('---------------------------------------------------------')
        print('Shape of Dataframe - {}'.format(df.shape))
        print('---------------------------------------------------------')
        print('\n Dataframe Info: \n')
        print('n{}'.format(df.info()))
        print('---------------------------------------------------------')
        print(' Categorical Features Stats: \n \n{}'.format(df.describe(include='O')))
        print('-------------------------------------------------')
        print(' Numerical Features Stats:- \n \n{}'.format(df.describe()))
              
    def _check_nan(self, df):
        '''Checks and verifies presence of null values in Dataframe'''
        nan = np.sum(df.isna().sum())
        if nan == 0:
            print('\n\n : There are no null values in the dataframes')
        else:
            print('The following columns have null values\n\n{}'.format(df.isnull().sum()))
              
    def _cat_cols(self, df):
        '''finds and lists Categorical Columns in Dataframe'''
        self.cat_cols = df.select_dtypes(include=['O']).columns.tolist()
        print('Categorical Columns list: {}'.format(self.cat_cols))
        print('---------------------------------------------------------------------')
        return self.cat_cols
              
    def _num_cols(self, df):
        '''finds and lists Numerical Columns in Dataframe'''
        self.num_cols = df.select_dtypes(exclude=['O']).columns.tolist()
        print('Numerical Columns list: {}'.format(self.num_cols))
        print('---------------------------------------------------------------------')
        return self.num_cols
              
              
    def _check_duplicates(self):
        '''Checks presence of duplicate entries'''
        print('\n : There are {} duplicate values in the Dataframe'.format(self.df.duplicated().sum()))
        
        
