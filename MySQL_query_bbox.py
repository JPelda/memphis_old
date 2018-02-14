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

engine = create_engine('mysql+pymysql://root:wasteheat@localhost:3306/spatial',
                       echo=False)
test = ox.gdf_from_place('Göttingen')
geo = test['geometry']
geo = geo.bounds
#print(geo.values[0])
#print(geo.to_string(index=False))
#print(geo['minx'].item())
#geo = [9.8001329, 51.4830052, 10.0536032, 51.5908839]
con_spatial = pymysql.connect(host='localhost', user='root',
                             password='wasteheat', db='spatial')

cur_spatial = con_spatial.cursor()

#query = ("SELECT * FROM `roads_ns` "
#                 " WHERE ST_ASText(SHAPE) "
#                 " && ST_Envelope({}, {}, {}, {}, 4326)").format(
#                         geo['minx'].to_string(index=False),
#                         geo['miny'].to_string(index=False),
#                         geo['maxx'].to_string(index=False),
#                         geo['maxy'].to_string(index=False))

bbox = ("ST_GEOMFROMTEXT('POLYGON(({} {},{} {},{} {},{} {},{} {}))')").format(
        geo['minx'].item(), geo['miny'].item(),
        geo['maxx'].item(), geo['miny'].item(),
        geo['maxx'].item(), geo['maxy'].item(),
        geo['minx'].item(), geo['maxy'].item(),
        geo['minx'].item(), geo['miny'].item())
#                         
print(bbox)
#print(query_spatial)
query_spatial = ("SELECT ST_ASText(SHAPE), osm_id, name FROM `roads_ns` "
                 " WHERE name = {}").format("'Drosselgasse'")

query_spatial = ("SELECT osm_id, ST_ASText(SHAPE), name From `roads_ns` WHERE MBRContains({}, ST_GeomFromText(ST_ASText(SHAPE))) = 1").format(bbox)
#df = pd.read_sql_query(query_spatial, con=engine)

cur_spatial.execute(query_spatial)


query_save = ("Create Table goettingen Select "
              " osm_id, code, fclass, name, SHAPE, OGR_FID, maxspeed "
              " FROM `roads_ns` WHERE "
              " MBRContains({}, ST_GeomFromText(ST_ASText(SHAPE))) = 1"
              ).format(bbox)
cur_spatial.execute(query_save)
print(df)

#
#cur_spatial.execute("SELECT osm_id FROM `roads_ns` WHERE Contains('POLYGON((9.8001329 51.4830052,10.0536032 51.4830052,10.0536032 51.5908839,9.8001329 51.5908839,9.8001329 51.4830052))',ST_ASText(SHAPE))")
#print(cur_spatial.fetchone())


cur_spatial.close()
con_spatial.close()