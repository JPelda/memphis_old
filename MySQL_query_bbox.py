# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 13:48:26 2018

@author: jpelda
"""

import pymysql
import osmnx as ox
import sqlalchemy as sqla


from shapely.geometry import LineString, Point

test = ox.gdf_from_place('Göttingen')
geo = test['geometry']
geo = geo.bounds
print(geo.values[0])
#print(geo.to_string(index=False))
print(geo['minx'].item())

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
bbox = ('ST_Envelope([{},{},{},{},{}])').format(
                         Point(geo['minx'].item(),
                          geo['miny'].item()),
                         Point(geo['maxx'].item(),
                          geo['miny'].item()),
                         Point(geo['maxx'].item(),
                          geo['maxy'].item()),
                         Point(geo['minx'].item(),
                          geo['maxy'].item()),
                         Point(geo['minx'].item(),
                          geo['miny'].item()))
                         
bbox = ("ST_Boundary({})").format(geo.values[0])
print(bbox)
query = ("SELECT * FROM `roads_ns` "
         " WHERE ST_Contains({}, {})").format(bbox,'ST_ASText(SHAPE)')
print(query)
query_spatial = ("SELECT ST_LineFromText(ST_ASText(SHAPE), 0), osm_id, name FROM `roads_ns` "
                 " WHERE name = {}").format("'Drosselgasse'")
cur_spatial.execute(query_spatial)
print(cur_spatial.fetchone())
cur_spatial.execute("SELECT osm_id FROM `roads_ns` WHERE ST_Contains(ST_Envelope('POLYGON("
                    "(9.8001329 51.4830052,10.0536032 51.4830052, "
                    "10.0536032 51.5908839,9.8001329 51.5908839, "
                    "9.8001329 51.4830052))'),ST_ASText(SHAPE))")
print(cur_spatial.fetchone())
#cur_spatial.execute(query)


cur_spatial.close()
con_spatial.close()