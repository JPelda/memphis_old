# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 10:40:53 2018

@author: jpelda
"""

import configparser as cfp
import pandas as pd
from sqlalchemy import create_engine

class Data_IO:
    def __init__(self, fname_config):
        self.config = cfp.ConfigParser()
        self.config.read(fname_config)
        self.engine = create_engine(self.config['SQL']['db'], echo=False)

    def write_to_sqlServer(self, table_name, df):

        df.to_sql(table_name, self.engine, if_exists='replace')
        ('Saved Data to {} in db {}'.format(table_name, self.engine))

    def read_from_sqlServer(self, sql_query):
        '''
        Reads SQL-Database into pandas dataframe, which is worked on.
        Input:
            sql_query: name of sql-query in section SQL_QUERIES in config-file
        '''
        sql = self.config['SQL_QUERIES'][sql_query]
        df = pd.read_sql(eval(sql), self.engine)
        return df


if __name__ == "__main__":

    import os

    config = os.path.dirname(os.getcwd()) + os.sep +\
            'config' + os.sep + 'test_config.ini'

    Data = Data_IO(config)

    df = Data.read_from_sqlServer('gis')

    Data.write_to_sqlServer('test', df)
    
else:
    print('Data_IO')
