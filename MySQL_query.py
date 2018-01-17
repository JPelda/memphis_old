
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 21:18:19 2018

@author: jpelda
"""
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import os
import pymysql

from pyproj import Proj, transform




def transform_coordinates(x_list, y_list, from_CS='epsg:4326', into_CS='epsg:3035'):
    xy = transform(Proj(init=from_CS), Proj(init=into_CS), x_list, y_list)
    return xy[0], xy[1]



if __name__ == "__main__":
    x = [9.915804, 9.945415, 9.915804, 9.945415]
    y = [51.54128, 51.54128, 51.52927, 51.52927]

    x_3035, y_3035 = transform_coordinates(x, y)
    print(min(x_3035), min(y_3035))
    print(max(x_3035), max(y_3035))

    cnx = pymysql.connect(host='localhost', user='root',
                             password='wasteheat', db='test')
    cursor = cnx.cursor()
    engine = create_engine('mysql+pymysql://root:wasteheat@localhost:3306/test',
                           echo=False)
    
    query = ("SELECT * FROM memphis.census_ger WHERE x_mp_100m BETWEEN {} "
             "AND {} AND y_mp_100m BETWEEN {} AND {}").format(min(x_3035),
                  max(x_3035), min(y_3035), max(y_3035))
    #cursor.execute(query)
    df = pd.read_sql_query(query, con=engine)
    print(df)

    x_4326, y_4326 = transform_coordinates(df['x_mp_100m'][0],
                                                  df['y_mp_100m'][0],
                                                  from_CS='epsg:3035',
                                                  into_CS='epsg:4326')
    print(x_4326, y_4326)
    #val = 4
    #cursor.execute(query, (val))
    #
    #for (ich, du) in cursor:
    #    print("ich {}, du {}".format(ich, du))
else:
    pass