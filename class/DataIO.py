# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 10:40:53 2018

@author: jpelda
"""

import configparser as cfp
import pandas as pd
from sqlalchemy import create_engine


class DataIO:
    def __init__(self, fname_config):
        config = cfp.ConfigParser()
        con = config.read(fname_config)
        self.engine = create_engine(con['SQL']['db'], echo=False)

    def write_to_sqlServer(self, name, df):
        df.to_sql(name, self.engine, if_exists='replace')
        ('Saved Data to {} in db {}'.format(name, self.engine))

    def read_from_sqlServer(self, sql_query, engine):
        # calls(sql_query), transforms it into pandas.DataFrame()
        # execute sql_query
        # save sql_query result into df
        # return df
        df = pd.read_sql(self.engine)
        return df

if __name__ == "__main__":
    print('main')

else:
    print('else frm DataIO')
