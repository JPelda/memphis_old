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

sys.path.append(os.getcwd() + os.sep + 'class')
sys.path.append(os.getcwd() + os.sep + 'func')
from Data_IO import Data_IO
from Conditioning import Conditioning
from Allocation import Allocation
#  TODO reproject data with geopandas better than transform coordinates?

#########################################################################
# LOAD DATA
#########################################################################

config = os.getcwd() + os.sep +\
        'config' + os.sep + 'test_config.ini'
Data = Data_IO(config)

gis = Data.read_from_sqlServer('gis')
census = Data.read_from_sqlServer('census')

census_gdf = gpd.GeoDataFrame(census, crs=Data.coord_system, geometry='geo')
gis_gdf = gpd.GeoDataFrame(gis, crs=Data.coord_system, geometry='geo')


#########################################################################
# C O N D I T I O N I N G
#########################################################################
s_time = time.time()

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
                        point in census['geo']]
inhabitans = [x for x in census['inhabitans']]

raster = {'geo': poly, 'inhabitans': inhabitans}
raster = gpd.GeoDataFrame(raster, crs=Data.coord_system, geometry='geo')

point = [Point(Data.xMin, Data.yMin)]
point = [poly[19]]
test = {'geo': point}

test = gpd.GeoDataFrame(test, crs=Data.coord_system, geometry='geo')

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


#census_gdf.plot(ax=ax)
gis_gdf.plot(ax=ax, color='black', linewidth=0.3, alpha=1)

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
#test.plot(ax=ax, color="red", alpha=1)
plt.show()
fig.savefig('Göttingen' + '.pdf',
            filentype='pdf', bbox_inches='tight', dpi=600)
