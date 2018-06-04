# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 10:36:21 2018

@author: jpelda
"""

import os
import sys

import time
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

import osmnx
import numpy as np
import matplotlib.lines as mlines
from matplotlib.colors import from_levels_and_colors
from matplotlib.ticker import FormatStrFormatter

sys.path.append(os.getcwd() + os.sep + 'src')
sys.path.append(os.getcwd() + os.sep + 'src' + os.sep + 'utils')

from Data_IO import Data_IO
from Conditioning import Conditioning
from Allocation import Allocation
from wcPERinhab import wcPERinhab
from merge_points import merge_points
from transformations_of_crs_values import transform_coords, meter_to_crs_length
from plotter import plot_format, color_map
from buffer import buffer
from Allocation import Allocation
from accumulate_val_along_path import sum_wc
from paths_to_dataframe import paths_to_dataframe
from shortest_paths import shortest_paths
from Equations import Conversions
from Evaluation import Clustering
#  TODO reproject data with geopandas better than transform coordinates?

#########################################################################
# LOAD DATA
#########################################################################
print("load data")
s_time = time.time()

Data = Data_IO('config' + os.sep + 'test_config.ini')
alloc = Allocation()


gis_r = Data.read_from_sqlServer('gis_roads')
gdf_gis_r = gpd.GeoDataFrame(gis_r, crs=Data.coord_system, geometry='SHAPE')

gis_b = Data.read_from_sqlServer('gis_buildings')
gdf_gis_b = gpd.GeoDataFrame(gis_b, crs=Data.coord_system, geometry='SHAPE')

wc = Data.read_from_sqlServer('wc_per_inhab')
wc = wc.drop(0)
wc['lPERpTIMESh'] = wc['lPERpTIMESd'].astype(float) / 1000 / 24

graph = Data.read_from_graphml('graph')
intersection_centroids = osmnx.simplify.clean_intersections(
        graph, tolerance=meter_to_crs_length(20), dead_ends=False)

census = Data.read_from_sqlServer('census')
gdf_census = gpd.GeoDataFrame(census, crs=Data.coord_system, geometry='SHAPE')

pipes_table = Data.read_from_sqlServer('pipes_dn_a_v_v')
pipes_table['V'] = pipes_table['V'] / 1000
pipes_table = {DN: {'A': A, 'v': v, 'V': V} for DN, A, v, V in
               zip(pipes_table.DN, pipes_table.A,
                   pipes_table.v, pipes_table.V)}

sew_net = Data.read_from_sqlServer('sewage_network')
sew_net = sew_net[sew_net['type'] == 'Schmutzwasserkanal']
sew_net['s_height'] = sew_net['s_height'].str.replace(',', '.')
sew_net['e_height'] = sew_net['e_height'].str.replace(',', '.')
sew_net['length'] = sew_net['length'].str.replace(',', '.')
sew_net['depth'] = sew_net['depth'].str.replace(',', '.')

sew_net['s_height'] = sew_net['s_height'].astype(float)
sew_net['e_height'] = sew_net['e_height'].astype(float)
sew_net['length'] = sew_net['length'].astype(float)
sew_net['depth'] = sew_net['depth'].astype(float)
sew_net['DN'] = sew_net['width'] / 1000
sew_net['height'] = sew_net['height'] / 1000
#sew_net = sew_net.fillna(1)

conv = Conversions()
sew_net['V'] = conv.DN_to_V(sew_net)
gdf_sewnet = gpd.GeoDataFrame(sew_net, crs=Data.coord_system, geometry='SHAPE')


print("gdf_sewnet.V {}".format(gdf_sewnet.V.isna().values.any()))
path = r"C:\Users\jpelda\Desktop\Stanet FW Stand 2011\shapefile"
dhs = Data.read_from_shp('dhs', path=path)
dhs['geometry'] = transform_coords(dhs.geometry, from_coord='epsg:5677')
gdf_dhs = gpd.GeoDataFrame(dhs, crs=Data.coord_system, geometry='geometry')

#########################################################################
# C O N D I T I O N I N G
#########################################################################
print('conditioning')
gdf_nodes, gdf_edges = osmnx.save_load.graph_to_gdfs(graph, nodes=True,
                                                     edges=True,
                                                     node_geometry=True,
                                                     fill_edge_geometry=True)


# Builds buffer around points of census.
gdf_census['SHAPE_b'] = buffer(gdf_census, Data.x_min, Data.x_max,
                               Data.y_min, Data.y_max)

#########################################################################
# A L L O C A T I O N
#########################################################################

# Allocates inhabitans of census to nodes of graph and multiplies them by
# water consumption of previous specified country.

print('allocation')
gdf_nodes['inhabs'] = alloc.alloc_inhabs_to_nodes(gdf_census, gdf_nodes, graph)
gdf_nodes['wc'] = gdf_nodes['inhabs'] *\
                         wc[wc.country_l == Data.country].lPERpTIMESh.item() *\
                         1.6

# Sets node of graph that is nearest to waste water treatment plant and
# calculates paths from nodes where nodes['inhabs'] > 0.
end_node = osmnx.get_nearest_node(graph, (Data.wwtp.y, Data.wwtp.x))
gdf_nodes['path_to_end_node'] = shortest_paths(graph, gdf_nodes, end_node)

# Accumulates wc along each path.
gdf_nodes['V'] = sum_wc(gdf_nodes)

# Generates GeoDataFrame from all paths with its attributes. Introduces the
# waterflow for each path by respecting the flow direction.
gdf_paths = paths_to_dataframe(gdf_nodes, gdf_edges)
pipes_table_V_to_DN = {val['V']: key for key, val in
                       zip(pipes_table.keys(), pipes_table.values())}
DN = np.array(list(pipes_table_V_to_DN.values()))
V_key = np.array(list(pipes_table_V_to_DN.keys()))
arr = [DN[np.where(V_key - V >= 0)[0][0]] if np.any(V_key - V > 0) else
       DN[-1] for V in gdf_paths['V']]
gdf_paths['DN'] = arr


##########################################################################
# E V A L U A T I O N
##########################################################################
print('\nevaluation')

geo0 = [x[0] for x in gdf_sewnet['SHAPE'].boundary]
geo1 = [x[1] for x in gdf_sewnet['SHAPE'].boundary]
V = np.append(gdf_sewnet['V'].values, gdf_sewnet['V'].values)
d = {'geometry': geo0 + geo1, 'V': V}
df = pd.DataFrame(data=d)
gdf_pts_sewnet = gpd.GeoDataFrame(df, crs=Data.coord_system,
                                  geometry='geometry')

geo0 = [x[0] for x in gdf_paths.geometry.boundary]
geo1 = [x[1] for x in gdf_paths.geometry.boundary]
V = np.append(gdf_paths.V.values, gdf_paths.V.values)
d = {'geometry': geo0 + geo1, 'V': V}
df = pd.DataFrame(data=d)
gdf_pts_paths = gpd.GeoDataFrame(df, crs=Data.coord_system,
                                 geometry='geometry')

gdf_census = gdf_census.set_geometry('SHAPE_b')
gdf_pts_sewnet['inhabs'] = alloc.alloc_nodes_to_inhabs(
        gdf_census, gdf_pts_sewnet)
gdf_pts_paths['inhabs'] = alloc.alloc_nodes_to_inhabs(
        gdf_census, gdf_pts_paths)
gdf_census = gdf_census.set_geometry('SHAPE')

# Getting distribution of points V to census inhabs
clust = Clustering()
keys = set(gdf_census.inhabs)
dis_sew_in_inh = clust.count_val_over_key(gdf_pts_sewnet, keys)
dis_pat_in_inh = clust.count_val_over_key(gdf_pts_paths, keys)
dis_cen_in_inh = clust.count_val_over_key(gdf_census, keys)

V_pat_comp_V_sew = clust.V_of_best_pts_within_overlay_pts(
        gdf_pts_paths, gdf_pts_sewnet, buffer=meter_to_crs_length(20))


#########################################################################
# V I S U A L I S A T I O N
#########################################################################
print('\nvisualisation')

fig0, ax0 = plt.subplots(figsize=(8 / 2.54, 4.5 / 2.54))
fig0.tight_layout(pad=0, w_pad=0, h_pad=0)
ax01 = ax0.twinx()
plot_format()
ax0.set_xlabel('Population density $[\\unitfrac{Persons}{10,000 m^2}]$')
ax0.set_ylabel('Amount of points')

ax0.set_yscale("log")
ax01.set_yscale("log")

width=1

print("Amount of sewages' points for inhabs = -1: {}".format(dis_sew_in_inh[-1]))
y = [dis_sew_in_inh[key] for key in sorted(dis_sew_in_inh.keys())]
ax0.bar(sorted(dis_sew_in_inh.keys()), y, color='green', width=width,
        label='Sewage network')

print("Amount of paths' points for inhabs = -1: {}".format(dis_pat_in_inh[-1]))
y = [dis_pat_in_inh[key] for key in sorted(dis_pat_in_inh.keys())]
ax0.bar(np.array(sorted(dis_pat_in_inh.keys())) + width+0.2, y, color='r',
        width=width, label='Generic sewage network')
handles0, labels0 = ax0.get_legend_handles_labels()

print("Amount of sewages' points for inhabs = -1: {}".format(dis_cen_in_inh[-1]))
y = [dis_cen_in_inh[key] for key in sorted(dis_cen_in_inh.keys())]
ax01.plot(sorted(dis_cen_in_inh.keys()), y, color='black', linestyle='',
         marker='_',
         label='Distribution of $[\\unitfrac{Persons}{10,000 m^2}]$')
handles01, labels01 = ax01.get_legend_handles_labels()

handles = handles0 + handles01
labels = labels0 + labels01

ax0.legend(handles, labels)


fig, ax = plt.subplots(figsize=(16 / 2.54, 9 / 2.54))
fig.tight_layout(pad=0, w_pad=0, h_pad=0)
plot_format()

# color_map()
# cmap_nodes = plt.get_cmap('WhiteRed')
# vmin_nodes = min(gdf_nodes['wc'])
# vmax_nodes = 100

ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))


levels = [-1, 0, 25, 50, 75, 100, 150, max(gdf_census['inhabs'])]
colors = ['white', '#C0C9E4', '#9EADD8', '#6D89CB',
          '#406DBB', '#3960A7', '#2F528F']
cmap_census, norm_census = from_levels_and_colors(levels, colors)

gdf_paths_levels = [0.01, max(gdf_paths['V'])]
gdf_paths_colors = ['r']
# cmap_paths, norm_paths = from_levels_and_colors(gdf_paths_levels,
#                                                gdf_paths_colors)

gdf_sewnet_levels = [0.01, max(gdf_sewnet['V'])]
gdf_sewnet_colors = ['green']
# cmap_sewnet, norm_sewnet = from_levels_and_colors(gdf_sewnet_levels,
#                                                  gdf_sewnet_colors)


sm_census = plt.cm.ScalarMappable(cmap=cmap_census, norm=norm_census)
sm_census._A = []
colorBar_census = fig.colorbar(sm_census, ax=ax)

census = gpd.GeoDataFrame(census, geometry='SHAPE_b', crs=Data.coord_system)
census.plot(ax=ax, cmap=cmap_census, norm=norm_census, column='inhabs',
            alpha=0.4)
colorBar_census.ax.set_ylabel("\\small{Inhabitants} "
                              "$[\\unitfrac{Persons}{10,000 m^2}]$",
                              fontsize=10)

gdf_gis_b_color = 'black'
gdf_gis_b_alpha = 0.2
gdf_gis_b.plot(ax=ax, color=gdf_gis_b_color, alpha=gdf_gis_b_alpha)
ax.plot(Data.wwtp.x, Data.wwtp.y, color='black', markersize=10,
        marker='*')

gdf_gis_r_color = 'black'
gdf_gis_r_alpha = 0.3
gdf_gis_r_linewidth = 0.3
gdf_gis_r.plot(ax=ax, color=gdf_gis_r_color, linewidth=gdf_gis_r_linewidth,
               alpha=gdf_gis_r_alpha)

gdf_paths[gdf_paths.V >= .01].plot(ax=ax, color='r', linewidth=1)
gdf_sewnet[gdf_sewnet.V >= .01].plot(ax=ax, color='green', linewidth=0.8)


# gdf_paths[gdf_paths.DN >= 800].plot(ax=ax, cmap=cmap_paths, norm=norm_paths,
#         column="DN", linewidth=1, )
# gdf_sewnet[gdf_sewnet.width >= 800].plot(ax=ax, cmap=cmap_sewnet,
#          norm=norm_sewnet, column="width", linewidth=0.8)
# for x, y, txt in zip(gdf_nodes['x'], gdf_nodes['y'], gdf_nodes.index):
#    ax.annotate(txt, (x, y))
# gdf_dhs.plot(ax=ax)

ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

wwtp_legend = mlines.Line2D([], [], color='black', marker='*',
                            linestyle='None', markersize=10,
                            label='Waste water treatment plant')
gdf_gis_b_legend = mlines.Line2D([], [], color=gdf_gis_b_color, marker='h',
                                 linestyle='None', markersize=10,
                                 label="Buildings", alpha=gdf_gis_b_alpha)
gdf_gis_r_legend = mlines.Line2D([], [], color=gdf_gis_r_color,
                                 linestyle='-', linewidth=gdf_gis_r_linewidth,
                                 label="Roads", alpha=gdf_gis_r_alpha)

gdf_sewnet_legend = []
gdf_sewnet_legend.append(
        mlines.Line2D(
                [], [], color=gdf_sewnet_colors[0],
                linestyle='-',
                label="Sewage network {:1.2f} "
                " $\\big[\\unitfrac{{m^3}}{{s}}\\big] "
                " \\leq \\dot{{V}}   \\leq$  {:10.2f}"
                " $\\big[\\unitfrac{{m^3}}{{s}}\\big]$"
                "".format(
                          gdf_sewnet_levels[0],
                          gdf_sewnet_levels[1])))
# gdf_sewnet_legend.append(mlines.Line2D([], [], color=gdf_sewnet_colors[1],
#                                  linestyle='-', label=
#                                  "Sewage network DN {} $\leq$ x $\leq$ DN {} "
#                                  "".format(
#                                        gdf_sewnet_levels[1],
#                                        gdf_sewnet_levels[2])))

legend_empty = [mlines.Line2D([], [], color='None', linestyle='')]
# ,                mlines.Line2D([], [], color='None', linestyle='')]
gdf_path_legend = []
gdf_path_legend.append(
        mlines.Line2D(
                [], [], color=gdf_paths_colors[0],
                linestyle='-',
                label="Generic sewage network {:1.2f} "
                " $\\big[\\unitfrac{{m^3}}{{s}}\\big] "
                " \\leq \\dot{{V}}   \\leq$  {:10.2f}"
                " $\\big[\\unitfrac{{m^3}}{{s}}\\big]$"
                "".format(
                          gdf_paths_levels[0],
                          gdf_paths_levels[1])))
# gdf_path_legend.append(mlines.Line2D([], [], color=gdf_paths_colors[1],
#                                linestyle='-',
#                                label=
#                                "Generic sewage network DN {} $\leq$ x $\leq$"
#                                " DN {}".format(
#                                        gdf_paths_levels[1],
#                                        gdf_paths_levels[2])))
# gdf_path_legend.append(mlines.Line2D([], [], color=gdf_paths_colors[2],
#                                linestyle='-',
#                                label=
#                                "Generic sewage network {} $\leq$ {:.0f}"
#                                " $[DN]$".format(
#                                        gdf_paths_levels[2],
#                                        gdf_paths_levels[3])))

handles = [wwtp_legend] + [gdf_gis_b_legend] + [gdf_gis_r_legend] +\
            gdf_sewnet_legend + gdf_path_legend

# Shrink current axis's height by 10% on the bottom
box = ax.get_position()
# ax.set_position([box.x0, box.y0 + box.height * 0.1,
#                 box.width, box.height * 0.9])

# ax.legend(handles=handles, loc='lower left', bbox_to_anchor=(0, -0.2),
#  ncol=3)

leg = ax.legend(handles=handles, bbox_to_anchor=(0.5, -0.15),
                borderaxespad=0.1, ncol=2, loc=9)
leg.get_frame().set_edgecolor('black')
leg.get_frame().set_linewidth(0.5)

plt.margins(0, 0, tight=True)
plt.show()


fig0.savefig('Amount_of_points_over_popDens.pdf', filetype='pdf',
             bbox_inches='tight', dpi=1200)
fig0.savefig('Amount_of_points_over_popDens.png', filetype='png',
             bbox_inches='tight', dpi=1200)

fig.savefig('Göttingen.pdf', filetype='pdf', bbox_inches='tight', dpi=1200)
fig.savefig('Göttingen.png', filetype='png', bbox_inches='tight', dpi=1200)



# del census['SHAPE_b']
# census = census.set_geometry('SHAPE')
# Data.write_gdf_to_file(census, 'census.shp')

Data.write_gdf_to_file(gdf_gis_b, 'gis_b.shp')
Data.write_gdf_to_file(gdf_gis_r, 'gis_r.shp')

# del gdf_paths['access']
# del gdf_paths['area']
# del gdf_paths['bridge']
# del gdf_paths['highway']
# del gdf_paths['junction']
# del gdf_paths['key']
# del gdf_paths['lanes']
# del gdf_paths['maxspeed']
# del gdf_paths['name']
# del gdf_paths['oneway']
# del gdf_paths['ref']
# del gdf_paths['service']
# del gdf_paths['tunnel']
# del gdf_paths['width']
# del gdf_paths['osmid']
# Data.write_gdf_to_file(gdf_paths, 'paths.shp')

del gdf_sewnet['geometry_b']
gdf_sewnet = gdf_sewnet.set_geometry('SHAPE')
Data.write_gdf_to_file(gdf_sewnet, 'sewnet.shp')


# fig.clear()

# Data.write_to_sqlServer('raster_visual', raster)
# Data.write_to_sqlServer('gis_visual', gis_gdf, dtype=)

# fig.savefig('Göttingen' + '.pdf',
#            filetype='pdf', bbox_inches='tight', dpi=600)


# Data.write_to_sqlServer('raster_visual', raster, dtype={
#        'SHAPE':'GEOMETRY', 'inhabitans':'int'})


# gis_gdf['name'] == None] = 
#  TODO NULL into sql as object and not string like here:
# gis_gdf.fillna(value='NULL', inplace=True)
# Data.write_to_sqlServer('gis_visual', gis_gdf, dtype={'osm_id':'int',
#                                                      'name':'varchar(100)',
#                                                      'SHAPE':'GEOMETRY'})

# folder = os.getcwd() + os.sep + 'input'
# osmnx.save_load.save_graph_shapefile(graph,'goettingen_graph', folder + os.sep)
# osmnx.save_load.save_gdf_shapefile(gdf_nodes, 'goettingen_graph', folder +
#                                   os.sep + 'goettingen_graph')
# osmnx.save_load.save_gdf_shapefile(gdf_edges, 'goettingen_graph', folder +
#                                   os.sep + 'goettingen_graph')
# osmnx.save_graphml(graph, 'goettingen.graphml', folder + os.sep)


