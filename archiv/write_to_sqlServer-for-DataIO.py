# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 17:04:37 2018

@author: adifischerson
"""
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import os
import pymysql
    


######################
# Write Centroid to DB
######################
cnx = pymysql.connect(host='localhost',
                          user='root',
                          password='wasteheat',
                          db='MEMPHIS_Output')
    
    cursor = cnx.cursor()
    engine = create_engine('mysql+pymysql://root:wasteheat@localhost:3306/MEMPHIS_Output',
                           echo=False)
    
df_geo.to_sql('centroid', engine, if_exists='replace', index=True)

#####################
# Write XY
#####################

