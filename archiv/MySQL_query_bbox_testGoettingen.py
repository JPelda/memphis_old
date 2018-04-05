# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 20:07:13 2018

@author: jpelda
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 13:48:26 2018

@author: jpelda
"""

import pymysql
import osmnx as ox
import sqlalchemy as sqla
from sqlalchemy import create_engine
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point

con = pymysql.connect(host='localhost', user='root',
                             password='wasteheat', db='memphis')

cur = con.cursor()
xMin = 9.90519
yMin = 51.5441
xMax = 9.93391
yMax = 51.5621

bbox = ("ST_GEOMFROMTEXT('POLYGON(({} {},{} {},{} {},{} {},{} {}))')").format(
        xMin, yMin, xMax, yMin, xMax, yMax, xMin, yMax, xMin, yMin)


query_save = ("Create Table buildings_goettingen Select "
              " OGR_FID, SHAPE, osm_id, code, fclass, name, type "
              " FROM `buildings_ns` WHERE "
              " MBRContains({}, ST_GeomFromText(ST_ASText(SHAPE))) = 1"
              ).format(bbox)
cur.execute(query_save)


#
#cur_spatial.execute("SELECT osm_id FROM `roads_ns` WHERE Contains('POLYGON((9.8001329 51.4830052,10.0536032 51.4830052,10.0536032 51.5908839,9.8001329 51.5908839,9.8001329 51.4830052))',ST_ASText(SHAPE))")
#print(cur_spatial.fetchone())


cur.close()
con.close()