# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 10:40:53 2018

@author: jpelda
"""

import pandas as pd
from sqlalchemy import create_engine

class DataIO:
    def __init__(self):
        pass

    def write_to_sqlServer(self, sql_query):
        pass

    def read_from_sqlServer(self, sql_query, engine):
        # TODO call(sql_query), transform result into pandas.DataFrame()
        # execute sql_query
        # save sql_query result into df
        # return df
        
        return df
    
    
    

if __name__ == "__main__":
    print('main')

else:
    print('else frm DataIO')