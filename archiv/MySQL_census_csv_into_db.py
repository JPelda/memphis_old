# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 12:54:19 2018

@author: jpelda
"""


from sqlalchemy import create_engine
import pandas as pd
import pymysql


CSV_FILE = "D:\jpelda\MEMPHIS\AIT\data\Zensus_Bevoelkerung_100m-Gitter.csv"

ID = 'grid_ID_100m'
x = 'x_mp_100m'
y = 'y_mp_100m'
val = 'inhabitans'

#cnx = pymysql.connect(host='localhost', user='root',
#                      password='wasteheat', db='test')
#cursor = cnx.cursor()
engine = create_engine('mysql+pymysql://root:wasteheat@localhost:3306/test',
                       echo=False)
#, 'census_ger_test'
#for table_name in ['census_ger']:
#    sql_create_table = (
#        "CREATE OR REPLACE TABLE `{}` ("
#        "`grid_ID_100m` varchar(20) NOT NULL,"
#        "`x_mp_100m` int(8) NOT NULL,"
#        "`y_mp_100m` int(8) NOT NULL,"
#        "`inhabitans` int(5) NOT NULL,"
#        "PRIMARY KEY (`x_mp_100m`,`y_mp_100m`), UNIQUE KEY `grid_ID_100m` "
#        "(`grid_ID_100m`) "
#        ")COLLATE='utf8_bin' ENGINE=MyISAM".format(table_name))
#    cursor.execute(sql_create_table)
#    cnx.commit()
#    print("Executed {}".format(sql_create_table))
#
#
#query = "LOAD DATA INFILE 'D:\\jpelda\\MEMPHIS\\AIT\\data\\Zensus_Bevoelkerung_100m-Gitter.csv' "\
#        "INTO TABLE `census_ger` "\
#        "FIELDS TERMINATED BY ';' ENCLOSED BY '\"' ESCAPED BY '\\\\'"
#print(query)
#try:
#    cursor.execute(query)
#    print("Executed {}".format(query))
#except:
#    pass
#
#cnx.commit()
#cursor.close()
#cnx.close()

pd.DataFrame()
fname = CSV_FILE
data_header = pd.read_csv(fname, delimiter=';', header=0, nrows=0)

data = pd.read_csv(fname, delimiter=';', names=[ID, x, y, val],
                   skiprows=1)


#chunksize = 1000000
#i = 0
#length = len(data)
#for i in range(0, length, chunksize):
#    pd.io.sql.to_sql(data[i:i+chunksize], name='census_ger',
#                     con=engine, index=False, index_label=ID,
#                     if_exists='append')
#    print('data left {}'.format(length - i), end='')
data.to_sql('census_ger', con=engine, index=False, if_exists='append',
            chunksize=10000000)
