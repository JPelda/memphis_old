# -*- coding: utf-8 -*-
"""
Created on Sat Jan  6 09:11:40 2018

@author: jpelda
"""

import pymysql
import sqlalchemy as sqla
import pyproj
from functools import partial
import shapely.ops
import shapely.wkt
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import igraph


from shapely.geometry import LineString, Point

con_spatial = pymysql.connect(host='localhost', user='root',
                             password='wasteheat', db='spatial')
con_memphis = pymysql.connect(host='localhost', user='root',
                             password='wasteheat', db='memphis')

cur_spatial = con_spatial.cursor()
cur_memphis = con_memphis.cursor()
engine = sqla.create_engine('mysql+pymysql://root:wasteheat@localhost:3306/spatial', echo=False)
#query = ("SELECT * FROM `spatial` WHERE osm_id = {} ").format(4262992)
query_spatial = ("SELECT ST_ASText(SHAPE), osm_id, name FROM `roads_ns` "
                 " WHERE name = {}").format("'Drosselgasse'")
#query_spatial = ("SELECT ST_ASText(SHAPE), osm_id, name FROM `roads_ns`")


cur_spatial.execute(query_spatial)
data = cur_spatial.fetchall()
print(data[2])
#  transform LINESTRING into shapely LINESTRING
ls = []
for item in data:
    ls.append(shapely.wkt.loads(item[0]))

#  generate list of tuple(coordinates) of LINESTRING
vs_max = 0
lstrings = []
index = 0

def pair(list):
    '''Iterate over pairs in a list -> pair of points '''
    for i in range(1, len(list)):
        yield list[i-1], list[i]

for geom in ls:
    for seg_start, seg_end in pair(geom.coords):
        line_start = Point(seg_start)
        line_end = Point(seg_end)
        segment = line_start.coords[0], line_end.coords[0]
        lstrings.append(segment)


#  generate dict of unique coordinates
keys0, keys1 = zip(*lstrings)
segments = keys0 + keys1
keys = set(tuple(segment) for segment in segments)
vs_dict = {key:index for index, key in enumerate(keys)}
print("{:21}{:4d}".format("Number of vertices: ", len(vs_dict)))

#  initialise edges by value given by vs_dict: input coordinate, ouput val
edges = [(vs_dict[key0], vs_dict[key1]) for key0, key1 in lstrings]
print("{:21}{:4d}".format("Number of edges: ", len(edges)))

G = igraph.Graph()
G.add_vertices(len(vs_dict))
G.add_edges(edges)
visual_style = {}
visual_style["vertex_size"] = 5
visual_style["vertex_shape"] = "circle"
visual_style["layout"] = 'lgl'
visual_style["bbox"] = (1024, 1024)
visual_style["margin"] = 10
layout = G.layout('kk')
fig = igraph.plot(G, layout=layout, vertex_size=3)
fig.show()




#    data.apply(shapely.wkb.loads)
#    data.ST_AsText(SHAPE) = shapely.wkt.loads(data.ST_AsText(SHAPE))
#    query_memphis = ("")

#    lstrings[0].apply
#    print(type(a))
#    print(a)
#    a.append(shapely.geometry.asLineString(lstrings[0]))
#    print(type(lstrings))
#    fig = plt.figure()
#    ax = fig.add_subplot(111)
#    gpd.plotting.plot_linestring_collection(ax, ls, color='blue')



#    x1_3035 = 4315158.675120066
#    y1_3035 = 3158964.723736821
#    project = partial(pyproj.transform,
#                        pyproj.Proj(init='epsg:4326'), # source coordinate system
#                        pyproj.Proj(init='epsg:3035')) # destination coordinate system

#except pymysql.Error as err:
#    print(err)

cur_memphis.close()
con_memphis.close()
cur_spatial.close()
con_spatial.close()
