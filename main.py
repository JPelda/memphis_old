# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 10:36:21 2018

@author: jpelda
"""

import os
import sys
sys.path.append(os.getcwd() + os.sep + 'class')

import geopandas as gpd
from Data_IO import Data_IO
from Conditioning import Conditioning
from Allocation import Allocation
import matplotlib.pyplot as plt
#  TODO reproject data with geopandas better than transform coordinates?

#########################################################################
# LOAD DATA
#########################################################################

config = os.getcwd() + os.sep +\
        'config' + os.sep + 'test_config.ini'
print('Load config from {}'.format(config))
Data = Data_IO(config)
gis = Data.read_from_sqlServer('gis')
census = Data.read_from_sqlServer('census')

census_gdf = gpd.GeoDataFrame(census, crs=Data.coord_system, geometry='geo')

gis_gdf = gpd.GeoDataFrame(gis, crs=Data.coord_system, geometry='geo')



#########################################################################
# C O N D I T I O N I N G
#########################################################################





#########################################################################
# A L L O C A T I O N
#########################################################################



#########################################################################
# V I S U A L I S A T I O N
#########################################################################
fig = plt.figure()
ax = fig.add_subplot(111)

census_gdf.plot(ax=ax)
gis_gdf.plot(ax=ax, color='red')

fig.show()
