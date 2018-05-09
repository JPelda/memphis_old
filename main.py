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
import configparser as cfp
from matplotlib.colors import ListedColormap


sys.path.append(os.getcwd() + os.sep + 'src')
print(os.getcwd() + os.sep + 'class')
sys.path.append(os.getcwd() + os.sep + 'src' + os.sep + 'utils')
from Data_IO import Data_IO
from Conditioning import Conditioning
from Allocation import Allocation
from wcPERinhab import wcPERinhab
from merge_points import merge_points
from transformations_of_crs_values import transform_coords
from plotter import plot_format, color_map
from buffer import buffer
from allocate_inhabitants_to_nodes import allocate_inhabitants_to_nodes
from accumulate_val_along_path import sum_wc
from paths_to_dataframe import paths_to_dataframe
#  TODO reproject data with geopandas better than transform coordinates?
# TODO implement logger, with time logging
# TODO Build intersections to all roads, then get shortest path.
#########################################################################
# LOAD DATA
#########################################################################
Data = Data_IO('config' + os.sep + 'test_config.ini')

# gis = Data.read_from_sqlServer('gis_roads')
# gdf_gis = gpd.GeoDataFrame(gis_roads, crs=Data.coord_system, geometry='SHAPE')
wc = Data.read_from_sqlServer('wc_per_inhab')
# Reads graph from file, shp import makes problems.
graph = Data.read_from_graphml('graph')
census = Data.read_from_sqlServer('census')


#########################################################################
# C O N D I T I O N I N G
#########################################################################

gdf_nodes, gdf_edges = osmnx.save_load.graph_to_gdfs(graph, nodes=True,
                                                     edges=True,
                                                     node_geometry=True,
                                                     fill_edge_geometry=True)


# Builds buffer around points of census.
gdf_census = gpd.GeoDataFrame(census, crs=Data.coord_system,
                              geometry='SHAPE')
gdf_census['SHAPE_b'] = buffer(gdf_census, Data.x_min, Data.x_max,
                               Data.y_min, Data.y_max)

#  TODO Do we really need to filter nodes for performance issues?
# singlepoints = merge_points([(id, geo) for id, geo in
#                             zip(gdf_nodes.osmid, gdf_nodes.geometry)],
#                            100)
# spoints = gpd.GeoDataFrame(singlepoints, columns=['osmid', 'SHAPE'],
#                           crs=Data.coord_system, geometry='SHAPE')


#########################################################################
# A L L O C A T I O N
#########################################################################

# Allocates inhabitans of census to nodes of graph and multiplies them by
# water consumption of previous specified country.
gdf_nodes['inhabs'] = allocate_inhabitants_to_nodes(gdf_census,
                                                    gdf_nodes, graph)
gdf_nodes['wc'] = gdf_nodes['inhabs'] *\
                         float(wc[wc.country_l ==
                                  Data.country].lPERpTIMESd.item())

# Sets node of graph that is nearest to waste water treatment plant and
# calculates paths from nodes where nodes['inhabs'] > 0.
end_node = osmnx.get_nearest_node(graph, (Data.wwtp.y, Data.wwtp.x))

gdf_nodes['path_to_end_node'] = [nx.shortest_path(graph, index, end_node) if
                                 row.wc != 0 else [] for index, row in
                                 gdf_nodes.iterrows()]

gdf_paths = paths_to_dataframe(gdf_nodes, gdf_edges)


# Accumulates wc along each path.
gdf_nodes['sum_wc'] = sum_wc(gdf_nodes)

# Allocates water flows to edges. Edge gets the value of the node with lowest
# wc
gdf_edges['sum_wc'] = [gdf_nodes.sum_wc[u] if
                       gdf_nodes.sum_wc[u] < gdf_nodes.sum_wc[v] else
                       gdf_nodes.sum_wc[v] for u, v in
                       zip(gdf_edges.u, gdf_edges.v)]


#########################################################################
# V I S U A L I S A T I O N
#########################################################################

fig, ax = plt.subplots()

color_map()
cmap_census = plt.get_cmap('WhiteRed')
cmap_nodes = plt.get_cmap('WhiteRed')
cmap_paths = plt.get_cmap('WhiteRed')
vmin_census = 0
vmax_census = 100
vmin_nodes = min(gdf_nodes['wc'])
vmax_nodes = 100
vmin_paths = 0
vmax_paths = 30000

sm_census = plt.cm.ScalarMappable(cmap=cmap_census,
                                  norm=plt.Normalize(vmin=vmin_census,
                                                     vmax=vmax_census))
sm_nodes = plt.cm.ScalarMappable(cmap=cmap_nodes,
                                 norm=plt.Normalize(vmin=vmin_nodes,
                                                    vmax=vmax_nodes))
sm_paths = plt.cm.ScalarMappable(cmap=cmap_paths,
                                 norm=plt.Normalize(vmin=vmin_paths,
                                                    vmax=vmax_paths))
sm_census._A, sm_nodes._A, sm_paths._A = [], [], []

colorBar_census = fig.colorbar(sm_census, ax=ax)
colorBar_nodes = fig.colorbar(sm_nodes, ax=ax)
colorBar_paths = fig.colorbar(sm_paths, ax=ax)

# gis_gdf.plot(ax=ax, color='black', linewidth=0.3, alpha=1)
census = gpd.GeoDataFrame(census, geometry='SHAPE_b', crs=Data.coord_system)
census.plot(ax=ax, cmap=cmap_census, vmin=vmin_census,
            vmax=vmax_census,
            column='inhabs',
            alpha=0.25)
#gdf_edges.plot(ax=ax, color='green', linewidth=0.4)
gdf_edges.plot(ax=ax, cmap=cmap_nodes, vmin=vmin_nodes, vmax=vmax_nodes,
               column='sum_wc', linewidth=0.3, alpha=0.3)

gdf_nodes.plot(ax=ax, cmap=cmap_nodes, vmin=vmin_nodes, vmax=vmax_nodes,
               column='wc', markersize=10)
#gdf_paths.plot(ax=ax, color='green')
gdf_nodes.plot(ax=ax, color='blue', markersize=5)
# for x, y, txt in zip(gdf_nodes['x'], gdf_nodes['y'], gdf_nodes['inhabs']):
# ax.annotate(txt, (x, y))

ax.plot(Data.wwtp.x, Data.wwtp.y, color='black', markersize=20,
        marker='.')

colorBar_census.ax.set_title('inhabitants', horizontalalignment='left',
                             fontsize=10)
colorBar_nodes.ax.set_title('inhabitants', horizontalalignment='left',
                            fontsize=10)

plt.show()

fig.savefig('Göttingen' + '.pdf',
            filetype='pdf', bbox_inches='tight', dpi=600)
#fig.clear()

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
#osmnx.save_load.save_graph_shapefile(graph,'goettingen_graph', folder + os.sep)
#osmnx.save_load.save_gdf_shapefile(gdf_nodes, 'goettingen_graph', folder +
#                                   os.sep + 'goettingen_graph')
#osmnx.save_load.save_gdf_shapefile(gdf_edges, 'goettingen_graph', folder +
#                                   os.sep + 'goettingen_graph')
#osmnx.save_graphml(graph, 'goettingen.graphml', folder + os.sep)

