# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 10:36:21 2018

@author: jpelda
"""

import os
import sys

import time
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point

import networkx as nx
import osmnx
from shapely.wkb import loads
import pandas as pd
import numpy as np

sys.path.append(os.getcwd() + os.sep + 'src')
print(os.getcwd() + os.sep + 'class')
sys.path.append(os.getcwd() + os.sep + 'src' + os.sep + 'utils')
from Data_IO import Data_IO
from Conditioning import Conditioning
from Allocation import Allocation
from wcPERinhab import wcPERinhab
from merge_points import merge_points
#  TODO reproject data with geopandas better than transform coordinates?

#########################################################################
# LOAD DATA
#########################################################################
start_time = time.time()
config = os.getcwd() + os.sep +\
        'config' + os.sep + 'test_config.ini'
Data = Data_IO(config)

#  TODO shift all the configparser into DATA_IO
import configparser as cfp
con = cfp.ConfigParser()
con.read(config)
country = con['SQL_QUERIES']['country']
wwtp = Point(float(con['coords']['waste_water_treatment_plant_x']),
             float(con['coords']['waste_water_treatment_plant_y']))

gdf_wwtp = gpd.GeoDataFrame([wwtp], columns=['SHAPE'],crs=Data.coord_system, geometry='SHAPE')

#gis = Data.read_from_sqlServer('gis')
census = Data.read_from_sqlServer('census')

#
#
#
#wc = Data.read_from_sqlServer('wc_per_inhab')
#
#census_gdf = gpd.GeoDataFrame(census, crs=Data.coord_system, geometry='SHAPE')
#gis_gdf = gpd.GeoDataFrame(gis, crs=Data.coord_system, geometry='SHAPE')
#wc_df = pd.DataFrame(wc)
#wcPERi = wcPERinhab(wc_df, 'Germany')

#gdf_edges = Data.read_from_shp('edges')
#gdf_nodes = Data.read_from_shp('nodes')
#print(gdf_edges)
#print(gdf_nodes)
#graph = osmnx.gdfs_to_graph(gdf_nodes, gdf_edges)
#folder = os.getcwd() + os.sep + 'input'
#graph = osmnx.graph_from_polygon(Data.bbox)
graph = Data.read_from_graphml('graph')

nx.set_node_attributes(graph, 0, name='inhabs')

##nodes = Data.read_from_sqlServer('graph_nodes')
##edges = Data.read_from_sqlServer('graph_edges')
#
##graph = osmnx.save_load.load_graphml()
#
##gdf_nodes = gpd.GeoDataFrame(nodes, crs=Data.coord_system, geometry="SHAPE")
##gdf_edges = gpd.GeoDataFrame(edges, crs=Data.coord_system, geometry="SHAPE")
#
#
gdf_nodes, gdf_edges = osmnx.save_load.graph_to_gdfs(
        graph,
        nodes=True, edges=True,
        node_geometry=True,
        fill_edge_geometry=True)

end_node = osmnx.get_nearest_node(graph, (wwtp.y, wwtp.x), method='haversine')
#end_node = end_node[0]

gdf_end_node = gpd.GeoDataFrame([gdf_nodes['geometry'][end_node]],
                                columns=['SHAPE'],
                                crs=Data.coord_system,
                                geometry='SHAPE')
shortest_paths = nx.shortest_path(graph, target=end_node)



#singlepoints = merge_points([(id, geo) for id, geo in
#                zip(gdf_nodes.osmid, gdf_nodes.geometry)],
#                100)

#spoints = gpd.GeoDataFrame(singlepoints, columns=['osmid', 'SHAPE'],
#                           crs=Data.coord_system, geometry='SHAPE')

#graph = osmnx.save_load.gdfs_to_graph(gdf_nodes, gdf_edges)

#gdf_edges['u_v'] = list(zip(gdf_edges.u, gdf_edges.v))
#print(gdf_edges['u_v'])

#print(graph)
#G = nx.MultiDiGraph()
#G.graph['crs'] = gdf_nodes.crs
#G.graph['name'] = gdf_nodes.gdf_name.rstrip('_nodes')
#
## add the nodes and their attributes to the graph
#G.add_nodes_from(gdf_nodes.index)
#attributes = gdf_nodes.to_dict()
#for attribute_name in gdf_nodes.columns:
#    # only add this attribute to nodes which have a non-null value for it
#    attribute_values = {k:v for k, v in attributes[attribute_name].items() if pd.notnull(v)}
#    nx.set_node_attributes(G, name=attribute_name, values=attribute_values)
#
## add the edges and attributes that are not u, v, key (as they're added
## separately) or null
#for _, row in gdf_edges.iterrows():
#    attrs = {}
#    for label, value in row.iteritems():
#        if (label not in ['u', 'v', 'key']) and (isinstance(value, list) or pd.notnull(value)):
#            attrs[label] = value
#    G.add_edge(row['u'], row['v'], attr_dict=attrs)
#print(G.edges[0]['access'])
#graph2 = osmnx.save_load.gdfs_to_graph(gdf_nodes, gdf_edges)


#########################################################################
# C O N D I T I O N I N G
#########################################################################

census_length_x = census['len_x'][0]
census_length_y = census['len_y'][0]
census_x_length = Data.xMax - Data.xMin
census_y_length = Data.yMax - Data.yMin

factor = 1.9
delta = census_x_length/census_length_x
border = delta / factor
delta_x = census_x_length/census_length_x - border
delta = census_y_length/census_length_y
border = delta / factor
delta_y = census_y_length/census_length_y - border

from transformations_of_crs_values import transform_coords
poly = [p.buffer(1, cap_style=3) for p in census['SHAPE']]
print(census['SHAPE'][0])
print(poly[0].exterior.coords.xy)
print(type(poly[0]))
coords = transform_coords([poly])
print(coords)
poly = [Polygon(((point.x - delta_x, point.y - delta_y),
                (point.x + delta_x, point.y - delta_y),
                (point.x + delta_x, point.y + delta_y),
                (point.x - delta_x, point.y + delta_y),
                (point.x - delta_x, point.y - delta_y))) for
                        point in census['SHAPE']]
inhabs = [x for x in census['inhabs']]

raster = {'SHAPE': poly, 'inhabs': inhabs}
raster = gpd.GeoDataFrame(raster, crs=Data.coord_system, geometry='SHAPE')
s_paths = shortest_paths



#  TODO search shortest path and accumulate each inhab of node at this path



#G = nx.Graph()
#G.add_nodes_from(gis_coords_doubles)
#nx.draw(G)
#########################################################################
# A L L O C A T I O N
#########################################################################

nearest_node = {}
for index, row in census.iterrows():
    node = osmnx.get_nearest_node(graph, (row['SHAPE'].y, row['SHAPE'].x))
    nearest_node[node] = row['inhabs']
for key in nearest_node.keys():
    graph.node[key]['inhabs'] = nearest_node[key]


#########################################################################
# V I S U A L I S A T I O N
#########################################################################

fig = plt.figure()
ax = fig.add_subplot(111)

gdf_nodes, gdf_edges = osmnx.save_load.graph_to_gdfs(
        graph,
        nodes=True, edges=True,
        node_geometry=True,
        fill_edge_geometry=True)

vmin = 0
vmax = 50
cmap = plt.cm.coolwarm
#raster.plot(ax=ax, cmap=cmap, vmin=vmin, vmax=vmax,
#            column='inhabitans', alpha=0.3)
sm = plt.cm.ScalarMappable(cmap=cmap,
                           norm=plt.Normalize(vmin=vmin, vmax=vmax))
sm._A = []
colorBar = plt.colorbar(sm)
#        colorBar.set_label("Q [kW]", horizontalalignment='right')
colorBar.ax.set_title('inhabitans',
                      horizontalalignment='left', fontsize=10)
#  test.plot(ax=ax, color="red", alpha=1)

#gis_gdf.plot(ax=ax, color='black', linewidth=0.3, alpha=1)
gdf_edges.plot(ax=ax, color='green', linewidth=0.3, alpha=1)
gdf_nodes.plot(ax=ax, cmap=cmap, vmin=vmin, vmax=vmax, column='inhabs',
               markersize=0.2)
gdf_wwtp.plot(ax=ax, color='blue', markersize=0.3)
gdf_end_node.plot(ax=ax, color='black', markersize=100)

#spoints['SHAPE'] = [x.buffer(0.0008959002216037959) for x in
#       spoints['SHAPE']]
#spoints.plot(ax=ax, color='blue')

vmin = 0
vmax = 50
cmap = plt.cm.coolwarm
#raster.plot(ax=ax, cmap=cmap, vmin=vmin, vmax=vmax,
#            column='inhabitans', alpha=0.3)
sm = plt.cm.ScalarMappable(cmap=cmap,
                           norm=plt.Normalize(vmin=vmin, vmax=vmax))
sm._A = []
colorBar = plt.colorbar(sm)
#        colorBar.set_label("Q [kW]", horizontalalignment='right')
colorBar.ax.set_title('inhabitans',
                      horizontalalignment='left', fontsize=10)
#  test.plot(ax=ax, color="red", alpha=1)
plt.show()

fig.savefig('Göttingen' + '.pdf',
            filetype='pdf', bbox_inches='tight', dpi=600)


#Data.write_to_sqlServer('raster_visual', raster)
#  Data.write_to_sqlServer('gis_visual', gis_gdf, dtype=)

#fig.savefig('Göttingen' + '.pdf',
#            filetype='pdf', bbox_inches='tight', dpi=600)


#Data.write_to_sqlServer('raster_visual', raster, dtype={
#        'SHAPE':'GEOMETRY', 'inhabitans':'int'})


#gis_gdf['name'] == None] = 
#  TODO NULL into sql as object and not string like here:
#gis_gdf.fillna(value='NULL', inplace=True)
#Data.write_to_sqlServer('gis_visual', gis_gdf, dtype={'osm_id':'int',
#                                                      'name':'varchar(100)',
#                                                      'SHAPE':'GEOMETRY'})

#folder = os.getcwd() + os.sep + 'input'
#osmnx.save_load.save_graph_shapefile(graph,'graph_goettingen', folder + os.sep)
#osmnx.save_load.save_gdf_shapefile(gdf_nodes, 'graph_goettingen', folder +
#                                   os.sep + 'graph_goettingen')
#osmnx.save_load.save_gdf_shapefile(gdf_edges, 'graph_goettingen', folder +
#                                   os.sep + 'graph_goettingen')
#osmnx.save_graphml(graph, 'graph_goettingen.graphml', folder + os.sep)

