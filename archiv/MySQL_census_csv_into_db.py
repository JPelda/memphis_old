# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 12:54:19 2018

@author: jpelda
"""
from datetime import date, datetime, timedelta
#import mysql.connector
#from mysql.connector import errorcode
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import os
import pymysql

print()

cnx = pymysql.connect(host='localhost', user='root',
                             password='wasteheat', db='test')
cursor = cnx.cursor()
engine = create_engine('mysql+pymysql://root:wasteheat@localhost:3306/test', echo=False)
#TABLES['census_ger'] = (
#        "CREATE TABLE `census_ger` ("
#        "  `grid_ID_100m` varchar(20) NOT NULL,"
#        "  `x_mp_100m` int(8) NOT NULL,"
#        "  `y_mp_100m` int(8) NOT NULL,"
#        "  `inhabitans` int(5) NOT NULL,"
#        "  PRIMARY KEY (`x_mp_100m`,`y_mp_100m`), UNIQUE KEY `grid_ID_100m` "
#        "  (`grid_ID_100m`) "
#        ") ENGINE=InnoDB")


#CSV_FILE = eval(os.path.dirname(os.getcwd()) + os.sep + "csv_Bevoelkerung_100m_Gitter" + os.sep + "Zensus_Bevoelkerung_100m-Gitter.csv")

query = "LOAD DATA INFILE 'census.csv' INTO TABLE census_ger FIELDS TERMINATED BY ';' ENCLOSED BY '\"' ESCAPED BY '\\\\'"
#load_data = "LOAD DATA INFILE `Zensus_Bevoelkerung_100m-Gitter.csv` INTO TABLE census_ger"
#df = pd.DataFrame(np.random.randint(low=0, high=10, size=(4, 4)),
#                  columns=['grid_ID_100m', 'x_mp_100m', 'y_mp_100m', 'inhabitans'])
ID = 'ID'
x = 'x'
y = 'y'
val = 'inhabitants'
pd.DataFrame()
fname = 'Zensus_Bevoelkerung_100m-Gitter.csv'
data_header = pd.read_csv(fname, delimiter=';', header=0, nrows=0)

data = pd.read_csv(fname, delimiter=';', names=[ID, x, y, val],
                   skiprows=1)
print(data)

#chunksize = 1000000
#i = 0
#for i in range(0, len(data), chunksize):
#    pd.io.sql.to_sql(data[i:i+chunksize], name='census_ger',
#                     con=engine, index=False, index_label='ID',
#                     if_exists='append')
#    print('\rdata left {}\r'.format(len(data) - i), end='')
#data.to_sql(name='census_ger', con=engine)

#cursor.execute(query)

# Make sure data is committed to the database
cnx.commit()
cursor.close()
cnx.close()
