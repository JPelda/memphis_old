# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 12:41:55 2018

@author: jpelda
"""

import pymysql
import osmnx as ox
import sqlalchemy as sqla
from sqlalchemy import create_engine
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point
import shapely.wkt
from matplotlib import pyplot as plt

city = "goettingen"
engine = create_engine('mysql+pymysql://root:wasteheat@localhost:3306/spatial',
                       echo=False)
con = pymysql.connect(host='localhost', user='root',
                             password='wasteheat', db='spatial')
cur = con.cursor()
query = ("SELECT osm_id, ST_ASText(SHAPE), name From {}").format(city)
cur.execute(query)
data = cur.fetchall()

df = pd.read_sql_query(query, engine)
#  transform LINESTRING into shapely LINESTRING
geo = df['ST_ASText(SHAPE)'].map(shapely.wkt.loads)
df = df.drop('ST_ASText(SHAPE)', axis=1)
crs = {'init': 'epsg:4326'}

gdf = gpd.GeoDataFrame(df, crs=crs, geometry=geo)
gdf.to_file('test.shp', driver='ESRI Shapefile')
fig = plt.subplot()
gdf.plot(ax=fig)
plt.savefig('test')