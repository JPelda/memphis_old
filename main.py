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

import osmnx
import numpy as np
from shapely.geometry import MultiPoint, MultiLineString, Polygon

sys.path.append(os.getcwd() + os.sep + 'src')
sys.path.append(os.getcwd() + os.sep + 'src' + os.sep + 'utils')

from Data_IO import Data_IO
from Allocation import Allocation
from transformations_of_crs_values import transform_coords, transform_length,\
                                          transform_area
from buffer import buffer
from accumulate_val_along_path import sum_wc
from paths_to_dataframe import paths_to_dataframe
from shortest_paths import shortest_paths
from Equations import Conversions
from Evaluation import Clustering
from Visualisation import Graphen

#########################################################################
# LOAD DATA
#########################################################################
print("load data")
s_time = time.time()

Data = Data_IO('config' + os.sep + 'goettingen.ini')
alloc = Allocation()

gis_r = Data.read_from_sqlServer('gis_roads')
gdf_gis_r = gpd.GeoDataFrame(gis_r, crs=Data.coord_system, geometry='SHAPE')

gis_b = Data.read_from_sqlServer('gis_buildings')
gdf_gis_b = gpd.GeoDataFrame(gis_b, crs=Data.coord_system, geometry='SHAPE')

gis_cat = Data.read_from_sqlServer('gis_categories')
gis_cat['cmPsma'] = gis_cat['cmPsma'].str.replace(',', '.')
gis_cat = gis_cat[gis_cat['cmPsma'] != '']
gis_cat = gis_cat[gis_cat['cmPsma'] != '?']
gis_cat['cmPsma'] = gis_cat['cmPsma'].astype(float)

gdf_gis_b['area'] = transform_area(gdf_gis_b.geometry)
gdf_gis_b['wc'] = alloc.alloc_wc_to_type(gis_cat, gdf_gis_b['type'].values) *\
                    gdf_gis_b['area'] / (8760 * 3600)


wc = Data.read_from_sqlServer('wc_per_inhab')
wc = wc.drop(0)
wc['cmPERpTIMESh'] = wc['lPERpTIMESd'].astype(float) / 1000 / (24 * 3600)

graph = Data.read_from_graphml('graph')

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

conv = Conversions()
sew_net['V'] = conv.DN_to_V(sew_net)
gdf_sewnet = gpd.GeoDataFrame(sew_net, crs=Data.coord_system, geometry='SHAPE')


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
geo0 = [x[0] for x in gdf_sewnet['SHAPE'].boundary]
geo1 = [x[1] for x in gdf_sewnet['SHAPE'].boundary]
mpt = MultiPoint(geo0 + geo1)
convex_hull = mpt.convex_hull
gdf_census = gdf_census[gdf_census.within(convex_hull)]
gdf_gis_r = gdf_gis_r[gdf_gis_r.within(convex_hull)]
gdf_gis_b = gdf_gis_b[gdf_gis_b.within(convex_hull)]

#########################################################################
# A L L O C A T I O N
#########################################################################

# Allocates inhabitans of census to nodes of graph and multiplies them by
# water consumption of previous specified country.

print('allocation')
gdf_nodes['inhabs'] = alloc.alloc_inhabs_to_nodes(gdf_census, gdf_nodes, graph)
gdf_nodes['wc'] = gdf_nodes['inhabs'] *\
                         wc[wc.country_l ==
                            Data.country].cmPERpTIMESh.item() * 1.6
gdf_nodes['wc'] += alloc.alloc_wc_from_b_to_node(gdf_gis_b, gdf_nodes, graph)

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
length = np.append(gdf_sewnet['length'].values, gdf_sewnet['length'].values)
d = {'geometry': geo0 + geo1, 'V': V, 'length': length}
df = pd.DataFrame(data=d)
gdf_pts_sewnet = gpd.GeoDataFrame(df, crs=Data.coord_system,
                                  geometry='geometry')

geo0 = [x[0] for x in gdf_paths.geometry.boundary]
geo1 = [x[1] for x in gdf_paths.geometry.boundary]
V = np.append(gdf_paths.V.values, gdf_paths.V.values)
length = np.append(gdf_paths['length'].values, gdf_paths['length'].values)
d = {'geometry': geo0 + geo1, 'V': V, 'length': length}
df = pd.DataFrame(data=d)
gdf_pts_paths = gpd.GeoDataFrame(df, crs=Data.coord_system,
                                 geometry='geometry')

gdf_census = gdf_census.set_geometry('SHAPE_b')
gdf_pts_sewnet['inhabs'], gdf_pts_sewnet['raster'] = alloc.alloc_nodes_to_inhabs(
        gdf_census, gdf_pts_sewnet)
gdf_pts_paths['inhabs'], gdf_pts_paths['raster'] = alloc.alloc_nodes_to_inhabs(
        gdf_census, gdf_pts_paths)

# Getting distribution of points V to census inhabs
clust = Clustering()
keys = set(gdf_census.inhabs)
dis_sew_in_inh = clust.count_val_over_key(gdf_pts_sewnet, keys)
dis_pat_in_inh = clust.count_val_over_key(gdf_pts_paths, keys)
dis_cen_in_inh = clust.count_val_over_key(gdf_census, keys)

pat_comp_V_sew = clust.best_pts_within_overlay_pts('V',
                                                   gdf_pts_paths,
                                                   gdf_pts_sewnet,
                                                   buffer=transform_length(20))

k = list(pat_comp_V_sew.keys())
k = [(k[i], k[i+1]) for i, item in enumerate(k) if i+1 < len(k)]
boxplot_V_over_V_pat = {key: [] for key in pat_comp_V_sew.keys()}
boxplot_V_over_V_sew = {key: [] for key in pat_comp_V_sew.keys()}
for tup in k:
    V_list = []
    for val in pat_comp_V_sew[tup[0]]:
        if not val.empty:
            V_list.append(val.V)
        else:
            V_list.append([])
    boxplot_V_over_V_pat[tup[0]] = V_list

    V_list = []
    arr = gdf_pts_sewnet[gdf_pts_sewnet.V > tup[0]]
    arr = arr[arr.V <= tup[1]]
    if not arr.empty:
        V_list.append(arr['V'].values)
    else:
        V_list.append([])
    boxplot_V_over_V_sew[tup[0]] = V_list


boxplot_length_over_V_pat = {key: [] for key in pat_comp_V_sew.keys()}
boxplot_length_over_V_sew = {key: [] for key in pat_comp_V_sew.keys()}
for tup in k:
    L_list = []
    for val in pat_comp_V_sew[tup[0]]:
        if not val.empty:
            L_list.append(val.length)
        else:
            L_list.append([])
    boxplot_length_over_V_pat[tup[0]] = L_list

    L_list = []
    leng = gdf_pts_sewnet[gdf_pts_sewnet.V > tup[0]]
    leng = leng[leng.V <= tup[1]]
    if not leng.empty:
        L_list.append(leng['length'].values)
    else:
        L_list.append([])
    boxplot_length_over_V_sew[tup[0]] = L_list


overlay_match = {}
overlay_sew = {}
overlay_pat = {}
for tup in k:
    m_ls_sew = gdf_sewnet[gdf_sewnet.V >= tup[0]]
    m_ls_sew = m_ls_sew[m_ls_sew.V < tup[1]]
    m_ls_pat = gdf_paths[gdf_paths.V >= tup[0]]
    m_ls_pat = m_ls_pat[m_ls_pat.V < tup[1]]

    m_ls_sew['geometry'] = m_ls_sew.buffer(transform_length(30))

    m_ls_sew = MultiLineString([(x) for x in m_ls_sew.geometry.values])
    m_ls_pat = MultiLineString([(x) for x in m_ls_pat.geometry.values])
    lines = m_ls_sew.intersection(m_ls_pat)

    overlay_match[tup[1]] = transform_length(
            np.sum(lines.length),
            crs_from="EPSG:4326",
            crs_into="EPSG:32633")
    overlay_sew[tup[1]] = transform_length(
            np.sum(m_ls_sew.length),
            crs_from="EPSG:4326",
            crs_into="EPSG:32633")
    overlay_pat[tup[1]] = transform_length(
            np.sum(m_ls_pat.length),
            crs_from="EPSG:4326",
            crs_into="EPSG:32633")

length_over_V_sew = {}
length_over_V_pat = {}

for tup in k:
    m_ls_sew = gdf_sewnet[gdf_sewnet.V >= tup[0]]
    m_ls_sew = m_ls_sew[m_ls_sew.V < tup[1]]
    m_ls_pat = gdf_paths[gdf_paths.V >= tup[0]]
    m_ls_pat = m_ls_pat[m_ls_pat.V < tup[1]]

    len_sew = transform_length(sum(m_ls_sew.geometry.length),
                               crs_from="EPSG:4326",
                               crs_into="EPSG:32633")
    len_pat = transform_length(sum(m_ls_pat.geometry.length),
                               crs_from="EPSG:4326",
                               crs_into="EPSG:32633")

    length_over_V_sew[tup[1]] = len_sew
    length_over_V_pat[tup[1]] = len_pat

#########################################################################
# V I S U A L I S A T I O N
#########################################################################
print('\nvisualisation')
vis = Graphen()

x_label = "$\\dot{V}$ of sewage network $[\\unitfrac{m^3}{s}]$"
y_label = "Distribution of $\\dot{V}$ of \ngeneric network $[\\unitfrac{m^3}{s}]$"
vis.plot_boxplot(boxplot_V_over_V_pat, Data.city,
                 name='boxplot_distr_V_over_V',
                 x_label=x_label, y_label=y_label, y_scale='log',
                 x_rotation=90, path_export=os.getcwd())

x_label = "$\\dot{V}$ $[\\unitfrac{m^3}{s}]$"
y_label = "Distribution of length [m]"
vis.plot_boxplot_2_in_1(boxplot_length_over_V_pat, boxplot_length_over_V_sew,
                        Data.city, name='boxplot_distr_length_over_V',
                        x_label=x_label, y_label=y_label, y_scale='log',
                        x_rotation=90, path_export=os.getcwd())

data = {'Sewage network': gdf_sewnet.V, 'Generic network': gdf_paths.V}
y_label = "Distribution of $\\dot{V}$ $[\\unitfrac{m^3}{s}]$"
vis.plot_boxplot(data, Data.city,
                 name='boxplot_distr_V', y_label=y_label, y_scale='log',
                 path_export=os.getcwd())

data = {'Sewage network': gdf_sewnet.length,
        'Generic network': gdf_paths.length}
y_label = "Distribution of edges' length [m]"
vis.plot_boxplot(data, Data.city,
                 name='boxplot_distr_length', y_label=y_label, y_scale='log',
                 path_export=os.getcwd())

vis.plot_distr_of_nodes(dis_sew_in_inh, dis_pat_in_inh, dis_cen_in_inh,
                        Data.city, 'amount_of_points_over_popDens',
                        path_export=os.getcwd())

vis.plot_map(gdf_census,
             gdf_paths[gdf_paths['V'] >= 0.01],
             gdf_sewnet[gdf_sewnet['DN'] >= 0.80], gdf_gis_b, gdf_gis_r,
             Data.coord_system, Data.city, Data.wwtp.x, Data.wwtp.y,
             path_export=os.getcwd())


geo0 = [x[0] for x in gdf_sewnet['SHAPE'][gdf_sewnet['DN'] >= 0.8].boundary]
geo1 = [x[1] for x in gdf_sewnet['SHAPE'][gdf_sewnet['DN'] >= 0.8].boundary]
geo2 = [x[0] for x in gdf_paths['geometry'][gdf_paths['V'] >= 0.01].boundary]
geo3 = [x[1] for x in gdf_paths['geometry'][gdf_paths['V'] >= 0.01].boundary]
mpt = MultiPoint(geo0 + geo1 + geo2 + geo3)

convex_hull = mpt.convex_hull
gdf_gis_b_cut = gdf_gis_b[gdf_gis_b.within(convex_hull)]
gdf_gis_r_cut = gdf_gis_r[gdf_gis_r.within(convex_hull)]
gdf_census_cut = gdf_census[gdf_census.within(convex_hull)]

vis.plot_map(gdf_census_cut, gdf_paths[gdf_paths['V'] >= 0.01],
             gdf_sewnet[gdf_sewnet['DN'] >= 0.80], gdf_gis_b_cut,
             gdf_gis_r_cut, Data.coord_system,
             Data.city + '_cut_ge_DN800', Data.wwtp.x, Data.wwtp.y,
             path_export=os.getcwd())

area = Polygon([[9.9336125704, 51.5358519306], [9.9619366976, 51.5358519306],
                [9.9619366976, 51.5469020742], [9.9336125704, 51.5469020742],
                [9.9336125704, 51.5358519306]])
gdf_gis_b_cut = gdf_gis_b[gdf_gis_b.within(area)]
gdf_gis_r_cut = gdf_gis_r[gdf_gis_r.within(area)]
gdf_census_cut = gdf_census[gdf_census.within(area)]
gdf_paths_cut = gdf_paths[gdf_paths.within(area)]
gdf_sewnet_cut = gdf_sewnet[gdf_sewnet.within(area)]

vis.plot_map(gdf_census_cut, gdf_paths_cut,
             gdf_sewnet_cut, gdf_gis_b_cut, gdf_gis_r_cut,
             Data.coord_system, Data.city + '_cut_area',
             area.centroid.x, area.centroid.y,
             path_export=os.getcwd(), paths_lw=3, sewnet_lw=1)

##########################
# SAVE
##########################


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

# del gdf_sewnet['geometry_b']
gdf_sewnet = gdf_sewnet.set_geometry('SHAPE')
Data.write_gdf_to_file(gdf_sewnet, 'sewnet.shp')

# Data.write_to_sqlServer('raster_visual', raster)
# Data.write_to_sqlServer('gis_visual', gis_gdf, dtype=)

# Data.write_to_sqlServer('raster_visual', raster, dtype={
#        'SHAPE':'GEOMETRY', 'inhabitans':'int'})

# folder = os.getcwd() + os.sep + 'input'
# osmnx.save_load.save_graph_shapefile(graph,'goettingen_graph',
# folder + os.sep)
# osmnx.save_load.save_gdf_shapefile(gdf_nodes, 'goettingen_graph', folder +
#                                   os.sep + 'goettingen_graph')
# osmnx.save_load.save_gdf_shapefile(gdf_edges, 'goettingen_graph', folder +
#                                   os.sep + 'goettingen_graph')
# osmnx.save_graphml(graph, 'goettingen.graphml', folder + os.sep)
