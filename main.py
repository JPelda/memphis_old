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
import matplotlib.lines as mlines
from matplotlib.colors import ListedColormap, from_levels_and_colors


sys.path.append(os.getcwd() + os.sep + 'src')
print(os.getcwd() + os.sep + 'class')
sys.path.append(os.getcwd() + os.sep + 'src' + os.sep + 'utils')
from Data_IO import Data_IO
from Conditioning import Conditioning
from Allocation import Allocation
from wcPERinhab import wcPERinhab
from merge_points import merge_points
from transformations_of_crs_values import transform_coords, meter_to_crs_length
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
Data = Data_IO('config' + os.sep + 'goettingen.ini')

gis_r = Data.read_from_sqlServer('gis_roads')
gdf_gis_r = gpd.GeoDataFrame(gis_r, crs=Data.coord_system, geometry='SHAPE')

gis_b = Data.read_from_sqlServer('gis_buildings')
gdf_gis_b = gpd.GeoDataFrame(gis_b,
                             crs=Data.coord_system, geometry='SHAPE')

wc = Data.read_from_sqlServer('wc_per_inhab')
# Reads graph from file, shp import makes problems.
graph = Data.read_from_graphml('graph')
intersection_centroids = osmnx.simplify.clean_intersections(
        graph, tolerance=meter_to_crs_length(20), dead_ends=False)
census = Data.read_from_sqlServer('census')

pipes_table = Data.read_from_sqlServer('pipes_dn_a_v_v')
pipes_table['V'] = pipes_table['V'] / 1000
pipes_table = {DN:{'A': A, 'v': v, 'V': V} for DN, A, v, V in
               zip(pipes_table.DN, pipes_table.A,
                   pipes_table.v, pipes_table.V)}

sew_net = Data.read_from_sqlServer('sewage_network')
sew_net = sew_net[sew_net['type'] == 'Schmutzwasserkanal']
gdf_sewnet = gpd.GeoDataFrame(sew_net, crs=Data.coord_system, geometry='SHAPE')
gdf_sewnet['V'] = [pipes_table.get(key, pipes_table[min(pipes_table.keys(),
                                   key=lambda k: abs(k-key))])['V'] for
                   key in gdf_sewnet['width']]


#########################################################################
# C O N D I T I O N I N G
#########################################################################
print('conditioning')
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

print('allocation')
gdf_nodes['inhabs'] = allocate_inhabitants_to_nodes(gdf_census,
                                                    gdf_nodes, graph)
gdf_nodes['wc'] = gdf_nodes['inhabs'] *\
                         float(wc[wc.country_l ==
                                  Data.country].lPERpTIMESd.item())

# Sets node of graph that is nearest to waste water treatment plant and
# calculates paths from nodes where nodes['inhabs'] > 0.
end_node = osmnx.get_nearest_node(graph, (Data.wwtp.y, Data.wwtp.x))

gdf_nodes['path_to_end_node'] = None
dic = {x: None for x in gdf_nodes.index}
s_time = time.time()

for m, (index, row) in enumerate(gdf_nodes.iterrows()):

    if row.wc != 0:

        values = dic[index]

        if values is None:

            print("\rLeft:{:>10}".format(len(gdf_nodes) - m), end='')

            try:
                values =\
                     nx.shortest_path(graph, index, end_node, weight='length')
                for i, n in enumerate(values):
                    dic[n] = values[i:]

            except nx.NetworkXNoPath:
                print("No path between {} and wastewater"
                      "treatment plant with node {}".format(index, end_node))
                dic[index] = []

    else:
        dic[index] = []

gdf_nodes['path_to_end_node'] = dic.values()
#print()
#print(time.time() - s_time)
#s_time = time.time()
#gdf_nodes['path_to_end_node'] = [nx.shortest_path(graph, index, end_node,
#                                 weight='length') if
#                                 row.wc != 0 else [] for index, row in
#                                 gdf_nodes.iterrows()]
#print(time.time() - s_time)


# Accumulates wc along each path.
gdf_nodes['sum_wc'] = sum_wc(gdf_nodes)

# Allocates water flows to edges. Edge gets the value of the node with lowest
# wc
gdf_edges['sum_wc'] = [gdf_nodes.sum_wc[u] if
                       gdf_nodes.sum_wc[u] < gdf_nodes.sum_wc[v] else
                       gdf_nodes.sum_wc[v] for u, v in
                       zip(gdf_edges.u, gdf_edges.v)]

gdf_paths = paths_to_dataframe(gdf_nodes, gdf_edges)

##########################################################################
## E V A L U A T I O N
##########################################################################
print('\nevaluation')
gdf_paths_index_geo_sumwc = {i: (geo, sumwc) for i, geo, sumwc in
                             zip(gdf_paths.index,
                                 gdf_paths.geometry,
                                 gdf_paths.sum_wc) if i != 0}
gdf_sewnet['geometry_b'] = gdf_sewnet.geometry.buffer(meter_to_crs_length(20))

vals = []
for index, (geo, width) in enumerate(zip(gdf_sewnet['geometry_b'],
                                         gdf_sewnet['width'])):
    arr = []
    print("\rLeft:{:>10}".format(len(gdf_sewnet) - index), end='')

    for i, item in gdf_paths_index_geo_sumwc.items():
        if item[0].intersects(geo):
            arr.append([i, item[1]])

    if arr != []:
        vals_keys = np.array([[x[0] for x in arr],
                        [y[1] for y in arr]])
        idx = (np.abs(vals_keys[1] - width)).argmin()
        del gdf_paths_index_geo_sumwc[vals_keys[0][idx]]
        vals.append(vals_keys[1][idx])
    else:
        vals.append(-1)

gdf_sewnet['V_generic'] = vals

dev = {key: {'mean': None, 'max': None, 'min': None, 'std': None} for
        key in set(gdf_sewnet['width'])}
V_dev = {key: {'mean': None, 'max': None, 'min': None, 'std': None} for
        key in set(gdf_sewnet['width'])}
V_generic_dev = {key: {'mean': None, 'max': None, 'min': None, 'std': None} for
        key in set(gdf_sewnet['width'])}

for wdt in dev:

    V = gdf_sewnet['V'][(gdf_sewnet['width'] == wdt) &
                        (gdf_sewnet['V_generic'] != -1)]
    V_g = gdf_sewnet['V_generic'][(gdf_sewnet['width'] == wdt) &
                                  (gdf_sewnet['V_generic'] != -1)]
    leng = len(V)
    if leng != 0:

        V_dev[wdt]['mean'] = sum(V) / leng
        V_dev[wdt]['max'] = max(V)
        V_dev[wdt]['min'] = min(V)
        V_dev[wdt]['std'] = np.std(V)
        
        V_generic_dev[wdt]['mean'] = sum(V_g) / leng
        V_generic_dev[wdt]['max'] = max(V_g)
        V_generic_dev[wdt]['min'] = min(V_g)
        V_generic_dev[wdt]['std'] = np.std(V_g)

        dff = (V - V_g) * 100 / V
        dev[wdt]['mean'] = sum(dff) / leng
        dev[wdt]['max'] = max(dff)
        dev[wdt]['min'] = min(dff)
        dev[wdt]['std'] = np.std(dff)


k = sorted(list(dev.keys()))
dev_mean = [dev[key]['mean'] for key in k]
V_mean = [V_dev[key]['mean'] for key in k]
V_generic_mean = [V_generic_dev[key]['mean'] for key in k]





#########################################################################
# V I S U A L I S A T I O N
#########################################################################
print('\nvisualisation')
fig, ax = plt.subplots()

plot_format()
#color_map()
#cmap_nodes = plt.get_cmap('WhiteRed')
#vmin_nodes = min(gdf_nodes['wc'])
#vmax_nodes = 100



levels = [-1, 0, 25, 50, 75, 100, 150, max(gdf_census['inhabs'])]
colors = ['white', '#C0C9E4', '#9EADD8', '#6D89CB',
          '#406DBB', '#3960A7', '#2F528F']
cmap_census, norm_census = from_levels_and_colors(levels, colors)

gdf_paths_levels = [0, 10000, 20000, max(gdf_paths['sum_wc'])]
gdf_paths_colors = ['lightsalmon', 'tomato', 'r']
cmap_paths, norm_paths = from_levels_and_colors(gdf_paths_levels,
                                                gdf_paths_colors)

gdf_sewnet_levels = [0, 800, max(gdf_sewnet['width'])]
gdf_sewnet_colors = ['greenyellow', 'green']
cmap_sewnet, norm_sewnet = from_levels_and_colors(gdf_sewnet_levels,
                                                  gdf_sewnet_colors)


sm_census = plt.cm.ScalarMappable(cmap=cmap_census, norm=norm_census)
sm_census._A = []
colorBar_census = fig.colorbar(sm_census, ax=ax)

census = gpd.GeoDataFrame(census, geometry='SHAPE_b', crs=Data.coord_system)
census.plot(ax=ax, cmap=cmap_census, norm=norm_census, column='inhabs',
            alpha=0.4)

gdf_gis_b_color = 'black'
gdf_gis_b_alpha = 0.2
gdf_gis_b.plot(ax=ax, color=gdf_gis_b_color, alpha=gdf_gis_b_alpha)
ax.plot(Data.wwtp.x, Data.wwtp.y, color='black', markersize=20,
        marker='*')

gdf_gis_r_color = 'black'
gdf_gis_r_alpha = 0.3
gdf_gis_r_linewidth = 0.3
gdf_gis_r.plot(ax=ax, color=gdf_gis_r_color, linewidth=gdf_gis_r_linewidth,
               alpha=gdf_gis_r_alpha)

gdf_paths.plot(ax=ax, cmap=cmap_paths, norm=norm_paths, column="sum_wc",
               linewidth=1)
gdf_sewnet.plot(ax=ax, cmap=cmap_sewnet, norm=norm_sewnet, column="width",
                linewidth=0.8)
# for x, y, txt in zip(gdf_nodes['x'], gdf_nodes['y'], gdf_nodes['inhabs']):
# ax.annotate(txt, (x, y))


ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

wwtp_legend = mlines.Line2D([], [], color='black', marker='*', linestyle='None',
                          markersize=10, label='Waste water treatment plant')
gdf_gis_b_legend = mlines.Line2D([], [], color=gdf_gis_b_color, marker='h',
                                 linestyle='None', markersize=10,
                                 label="Buildings", alpha=gdf_gis_b_alpha)
gdf_gis_r_legend = mlines.Line2D([], [], color=gdf_gis_r_color,
                                 linestyle='-', linewidth=gdf_gis_r_linewidth,
                                 label="Roads", alpha=gdf_gis_r_alpha)

gdf_sewnet_legend = []
gdf_sewnet_legend.append(mlines.Line2D([], [], color=gdf_sewnet_colors[0],
                                  linestyle='-', label=
                                  "Sewage network {} $\leq$ {} "
                                  "$[DN]$".format(
                                        gdf_sewnet_levels[0],
                                        gdf_sewnet_levels[1])))
gdf_sewnet_legend.append(mlines.Line2D([], [], color=gdf_sewnet_colors[1],
                                  linestyle='-', label=
                                  "Sewage network {} $\leq$ {} "
                                  "$[DN]$".format(
                                        gdf_sewnet_levels[1],
                                        gdf_sewnet_levels[2])))

legend_empty = [mlines.Line2D([], [], color='None', linestyle='')]
#,                mlines.Line2D([], [], color='None', linestyle='')]
gdf_path_legend = []
gdf_path_legend.append(mlines.Line2D([], [], color=gdf_paths_colors[0],
                                linestyle='-',
                                label=
                                "Waste water flows {} $\leq$ {} "
                                "$[\\unitfrac{{L}}{{d}}]$".format(
                                        gdf_paths_levels[0],
                                        gdf_paths_levels[1])))
gdf_path_legend.append(mlines.Line2D([], [], color=gdf_paths_colors[1],
                                linestyle='-',
                                label=
                                "Waste water flows {} $\leq$ {} "
                                "$[\\unitfrac{{L}}{{d}}]$".format(
                                        gdf_paths_levels[1],
                                        gdf_paths_levels[2])))
gdf_path_legend.append(mlines.Line2D([], [], color=gdf_paths_colors[2],
                                linestyle='-',
                                label=
                                "Waste water flows {} $\leq$ {:.0f}"
                                " $[\\unitfrac{{L}}{{d}}]$".format(
                                        gdf_paths_levels[2],
                                        gdf_paths_levels[3])))

handles = [wwtp_legend] + [gdf_gis_b_legend] + [gdf_gis_r_legend] +\
             gdf_sewnet_legend + legend_empty + gdf_path_legend

# Shrink current axis's height by 10% on the bottom
box = ax.get_position()
#ax.set_position([box.x0, box.y0 + box.height * 0.1,
#                 box.width, box.height * 0.9])

#ax.legend(handles=handles, loc='lower left', bbox_to_anchor=(0, -0.2),
#          ncol=3)
ax.legend(handles=handles, bbox_to_anchor=(1.45,1), borderaxespad=0, ncol=1)
colorBar_census.ax.set_title("Inhabitants "
                             "\n$[\\unitfrac{Persons}{10.000 m^2}]$",
                             horizontalalignment='left',
                             fontsize=10)

plt.margins(0,0, tight=True)
plt.show()

fig.savefig('Göttingen' + '.pdf',
            filetype='pdf', bbox_inches='tight', dpi=1200)

Data.write_gdf_to_file(census, 'census')
Data.write_gdf_to_file(gdf_gis_b, 'gis_b')
Data.write_gdf_to_file(gdf_gis_r, 'gis_r')
Data.write_gdf_to_file(gdf_paths, 'paths')
Data.write_gdf_to_file(gdf_sewnet, 'sewnet')


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


