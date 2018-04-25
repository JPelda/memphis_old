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
from matplotlib import rc
import networkx as nx
import osmnx
from shapely.wkb import loads
import pandas as pd

sys.path.append(os.getcwd() + os.sep + 'class')
print(os.getcwd() + os.sep + 'class')
sys.path.append(os.getcwd() + os.sep + 'func')
from Data_IO import Data_IO
from Conditioning import Conditioning
from Allocation import Allocation
from wcPERinhab import wcPERinhab
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

gis = Data.read_from_sqlServer('gis')
census = Data.read_from_sqlServer('census')
wc = Data.read_from_sqlServer('wc_per_inhab')

census_gdf = gpd.GeoDataFrame(census, crs=Data.coord_system, geometry='SHAPE')
gis_gdf = gpd.GeoDataFrame(gis, crs=Data.coord_system, geometry='SHAPE')
wc_df = pd.DataFrame(wc)

wcPERi = wcPERinhab(wc_df, 'Germany')



graph = osmnx.graph_from_polygon(Data.bbox)



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



poly = [Polygon(((point.x - delta_x, point.y - delta_y),
                (point.x + delta_x, point.y - delta_y),
                (point.x + delta_x, point.y + delta_y),
                (point.x - delta_x, point.y + delta_y),
                (point.x - delta_x, point.y - delta_y))) for
                        point in census['SHAPE']]
inhabitans = [x for x in census['inhabitans']]

raster = {'SHAPE': poly, 'inhabitans': inhabitans}
raster = gpd.GeoDataFrame(raster, crs=Data.coord_system, geometry='SHAPE')


#point = [Point(Data.xMin, Data.yMin)]
#point = [poly[19]]
#test = {'geo': point}
#
#test = gpd.GeoDataFrame(test, crs=Data.coord_system, geometry='geo')

#for line in gis_gdf['geo']:
#    for line1 in gis_gdf['geo']:
#        line.intersects(line1)

#G = nx.Graph()
#G.add_nodes_from(gis_coords_doubles)
#nx.draw(G)
#########################################################################
# A L L O C A T I O N
#########################################################################




#########################################################################
# V I S U A L I S A T I O N
#########################################################################
rc('text', usetex=True)
rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
#        rc('font', serif='malgunbd')
rc('ps', usedistiller='xpdf')
rc('pdf', fonttype=42)
rc('ps', fonttype=42)
rc('figure', figsize = [4, 2.25])
grid_linewidth = 0.3
xyLabelsize=8
labelsize = 8
rc('lines', lw = 1.3, c='r', ls='-', dash_capstyle='round',
   solid_capstyle='round')
rc('axes', grid=False, lw=grid_linewidth)
rc('grid', ls='dotted', lw=grid_linewidth, alpha=1)
rc('xtick', direction='in', labelsize=labelsize)
rc('xtick.major', width=grid_linewidth, size=5)
rc('xtick.minor', width=grid_linewidth, size=4)
rc('xtick', labelsize=xyLabelsize)
rc('ytick', direction='in', labelsize=labelsize)
rc('ytick.major', width=grid_linewidth, size=5)
rc('ytick.minor', width=grid_linewidth, size=4)
rc('ytick', labelsize=xyLabelsize)
rc('legend', fontsize='small')
fig = plt.figure()
ax = fig.add_subplot(111)



#graph_gdf_nodes, graph_gdf_edges = osmnx.save_load.graph_to_gdfs(
#        graph,
#        nodes=True, edges=True,
#        node_geometry=True,
#        fill_edge_geometry=False)

gis_gdf.plot(ax=ax, color='black', linewidth=0.3, alpha=1)
#graph_gdf_nodes.plot(ax=ax, color='red', markersize=0.2)
#graph_gdf_edges.plot(ax=ax, color='green', linewidth=0.3, alpha=1)

vmin = 0
vmax = 50
cmap = plt.cm.coolwarm
raster.plot(ax=ax, cmap=cmap, vmin=vmin, vmax=vmax,
            column='inhabitans', alpha=0.3)
sm = plt.cm.ScalarMappable(cmap=cmap,
                           norm=plt.Normalize(vmin=vmin, vmax=vmax))
sm._A = []
colorBar = plt.colorbar(sm)
#        colorBar.set_label("Q [kW]", horizontalalignment='right')
colorBar.ax.set_title('inhabitans',
                      horizontalalignment='left', fontsize=10)
#  test.plot(ax=ax, color="red", alpha=1)
plt.show()
<<<<<<< HEAD
fig.savefig('Göttingen' + '.pdf',
            filetype='pdf', bbox_inches='tight', dpi=600)


#Data.write_to_sqlServer('raster_visual', raster)
#  Data.write_to_sqlServer('gis_visual', gis_gdf, dtype=)
=======
#fig.savefig('Göttingen' + '.pdf',
#            filetype='pdf', bbox_inches='tight', dpi=600)


Data.write_to_sqlServer('raster_visual', raster, dtype={
        'SHAPE':'GEOMETRY', 'inhabitans':'int'})
print(gis_gdf.keys())
a = None
#gis_gdf['name'] == None] = 
#  TODO NULL into sql as object and not string like here:
gis_gdf.fillna(value='NULL', inplace=True)
Data.write_to_sqlServer('gis_visual', gis_gdf, dtype={'osm_id':'int',
                                                      'name':'varchar(100)',
                                                      'SHAPE':'GEOMETRY'})
>>>>>>> 2eff254be9c39934a66908e5e78fbd8e757d0258
#Data.write_to_sqlServer('graph_nodes', graph_gdf_nodes,
#                        dtype={'highway': 'varchar(20)',
#                               'osmid': 'int',
#                               'x': 'float',
#                               'y': 'float',
#                               'geometry': 'GEOMETRY'})
#Data.write_to_sqlServer('graph_edges', graph_gdf_edges,
#                        dtype={'access': 'varchar(10)',
#                               'area':
#                               'bridge': 'varchar(10)',
#                               'est_width': 'varchar(10)',
#                               'geometry': 'GEOMETRY',
#                               'highway': 'varchar(10)',
#                               'key': 'int',
#                               'lanes': 'varchar(10)',
#                               'length': 'float(6)',
#                               'maxspeed': 'int(3)',
#                               'name': 'varchar(20)',
#                               'oneway': 'bool',
#                               'osmid': 'int',
#                               'ref': 'varchar(15)',
#                               'service': 'varchar(20)',
#                               'tunnel': 'varchar(20)',
#                               'u': 'int',
#                               'v': 'int',
#                               'width': 'float'})
                        