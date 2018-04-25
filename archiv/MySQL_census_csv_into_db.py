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

#print()

cnx = pymysql.connect(host='localhost',
                      user='root',
                      password='wasteheat', 
                      db='memphis')

cursor = cnx.cursor()
engine = create_engine('mysql+pymysql://root:wasteheat@localhost:3306/memphis', echo=False)
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
print("pls wait about 20 min - then reload localhost")
query = "LOAD DATA INFILE 'E:/datamemphis/data/Zensus_Bevoelkerung_100m-Gitter.csv' INTO TABLE census_ger FIELDS TERMINATED BY ';' ENCLOSED BY '\"' ESCAPED BY '\\\\'"

cursor.execute(query)

# Make sure data is committed to the database
cnx.commit()
cursor.close()
cnx.close()
print("finished")

