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
#  TODO reproject data with geopandas better than transform coordinates?

#########################################################################
# LOAD DATA
#########################################################################
start_time = time.time()
config = os.getcwd() + os.sep +\
        'config' + os.sep + 'test_config.ini'
Data = Data_IO(config)

### Reads location of waste water treatment plant. ###
gdf_wwtp = gpd.GeoDataFrame([Data.wwtp], columns=['SHAPE'],
                             crs=Data.coord_system, geometry='SHAPE')

### Reads gis data. ###
#gis = Data.read_from_sqlServer('gis')
#gdf_gis = gpd.GeoDataFrame(gis, crs=Data.coord_system, geometry='SHAPE')

### Reads water consumption and thus waste water production. ###
wc = Data.read_from_sqlServer('wc_per_inhab')

### Reads graph from file, shp import makes problems. ###
graph = Data.read_from_graphml('graph')
nx.set_node_attributes(graph, 0, name='inhabs')
end_node = osmnx.get_nearest_node(graph, (Data.wwtp.y, Data.wwtp.x))
shortest_paths = nx.shortest_path(graph, target=end_node)
# TODO calc only paths for nodes as start node where node[inhab] > 0
gdf_nodes, gdf_edges = osmnx.save_load.graph_to_gdfs(
        graph,
        nodes=True, edges=True,
        node_geometry=True,
        fill_edge_geometry=True)

### Reads census data and builds buffer. ###
census = Data.read_from_sqlServer('census')
gdf_census = gpd.GeoDataFrame(census, crs=Data.coord_system,
                              geometry='SHAPE')
#geo = transform_coords(gdf_census['SHAPE'],
#                       from_coord='epsg:4326',
#                       into_coord="epsg:3035")
#geo = [x.buffer(40, cap_style=3) for x in geo]
#geo = transform_coords(geo)
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

geo = [Polygon(((point.x - delta_x, point.y - delta_y),
                (point.x + delta_x, point.y - delta_y),
                (point.x + delta_x, point.y + delta_y),
                (point.x - delta_x, point.y + delta_y),
                (point.x - delta_x, point.y - delta_y))) for
        point in census['SHAPE']]
gdf_census['SHAPE_b'] = geo
gdf_census['nodes_within'] = 0

p_within = [0]*len(gdf_census['nodes_within'])
gdf_nodes_osmid_geometry = {int(osmid): geo for osmid, geo in zip(
        gdf_nodes['osmid'], gdf_nodes['geometry'])}

for i, (point, poly, inhab) in enumerate(zip(gdf_census['SHAPE'],
                                             gdf_census['SHAPE_b'],
                                             gdf_census['inhabs'])):
    if inhab <= 0:
        continue
    else:
        p_within[i] = {osmid: inhab for osmid, p in
                       zip(gdf_nodes_osmid_geometry.keys(),
                           gdf_nodes_osmid_geometry.values()) if
                       p.within(poly)}
        if p_within[i] != {}:
            val = list(p_within[i].values())[0] / len(p_within[i])
            p_within[i] = dict.fromkeys(p_within[i], val)
            for key, val in p_within[i].items():
                gdf_nodes['inhabs'][key] += val
                del gdf_nodes_osmid_geometry[key]
        else:
            key = osmnx.get_nearest_node(graph, (point.y, point.x))
            gdf_nodes['inhabs'][key] += inhab


gdf_nodes['inhabs'] = gdf_nodes['inhabs'] *\
                         float(wc[wc.country_l ==
                                  Data.country].lPERpTIMESd.item())

G = osmnx.save_load.gdfs_to_graph(gdf_nodes, gdf_edges)


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


s_paths = shortest_paths
G_s_paths = nx.Graph()
routes = s_paths.values()

edges = []
for r in routes:
    route_edges = [(r[n],r[n+1]) for n in range(len(r)-1)]
    G.add_nodes_from(r)
    G.add_edges_from(route_edges)
    edges.append(route_edges)

gdf_paths_nodes, gdf_paths_edges = osmnx.save_load.graph_to_gdfs(G)




#########################################################################
# A L L O C A T I O N
#########################################################################


#for index, row in census.iterrows():
#    node = osmnx.get_nearest_node(graph, (row['SHAPE'].y, row['SHAPE'].x))
#    nearest_node[node] = row['inhabs']
#for key in nearest_node.keys():
#    graph.node[key]['inhabs'] = nearest_node[key]


#########################################################################
# V I S U A L I S A T I O N
#########################################################################

fig, ax = plt.subplots()

#vmin = 0
#vmax = 50
color_map()
#cmap = plt.cm.binary

cmap_census = plt.get_cmap('WhiteRed')
#cmap_with_alpha = cmap
#cmap_with_alpha = cmap(np.arange(cmap.N))
cmap_nodes = plt.get_cmap('WhiteRed')
cmap_paths = plt.get_cmap('WhiteRed')
#cmap_with_alpha[:, -1] = np.linspace(0, 1, cmap.N)
#cmap_with_alpha = ListedColormap(cmap_with_alpha)
#vmin = min(gdf_nodes['inhabs'])
vmin_census = 0
vmax_census = 100
vmin_nodes = min(gdf_nodes['inhabs'])
vmax_nodes = 100
vmin_paths = 0
vmax_paths = 300

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
#        colorBar.set_label("Q [kW]", horizontalalignment='right')


#gis_gdf.plot(ax=ax, color='black', linewidth=0.3, alpha=1)
census = gpd.GeoDataFrame(census, geometry='SHAPE_b', crs=Data.coord_system)
census.plot(ax=ax, cmap=cmap_census, vmin=vmin_census,
                        vmax=vmax_census,
                        column='inhabs',
                        alpha=0.25)

gdf_edges.plot(ax=ax, color='green', linewidth=0.3, alpha=1)

gdf_nodes.plot(ax=ax, cmap=cmap_nodes, vmin=vmin_nodes, vmax=vmax_nodes,
               column='inhabs', markersize=10)

gdf_paths_edges.plot(ax=ax, color='blue', linewidth=0.4)
#gdf_paths_nodes.plot(ax=ax, color=cmap_paths, vmin=vmin_paths, vmax=vmax_paths,
#                     column='inhabs', markersize=15)

#for x, y, txt in zip(gdf_nodes['x'], gdf_nodes['y'], gdf_nodes['inhabs']):
#    ax.annotate(txt, (x, y))

ax.plot(Data.wwtp.x, Data.wwtp.y, color='black', markersize=20,
        marker='.')

#nodes = {key: val for key, val in zip(gdf_nodes['osmid'],
#                                      gdf_nodes['geometry'])}
#nx.draw_networkx_nodes(G, nodes, ax=ax,
#                       cmap=cmap, vmin=vmin, vmax=vmax)

colorBar_census.ax.set_title('inhabitants',
                      horizontalalignment='left', fontsize=10)
colorBar_nodes.ax.set_title('inhabitants',
                            horizontalalignment='left', fontsize=10)

plt.show()
#plt.pause(5)
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
#osmnx.save_load.save_graph_shapefile(graph,'graph_goettingen', folder + os.sep)
#osmnx.save_load.save_gdf_shapefile(gdf_nodes, 'graph_goettingen', folder +
#                                   os.sep + 'graph_goettingen')
#osmnx.save_load.save_gdf_shapefile(gdf_edges, 'graph_goettingen', folder +
#                                   os.sep + 'graph_goettingen')
#osmnx.save_graphml(graph, 'graph_goettingen.graphml', folder + os.sep)

