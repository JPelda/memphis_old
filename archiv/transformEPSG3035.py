# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 10:22:33 2017

@author: jpelda
"""
from osgeo import ogr
from osgeo import osr
import osgeo
#import osgeo.ogr, osgeo.osr
#from osgeo import ogr

import os
import csv
import pandas as pd
import numpy as np
from pyproj import Proj, transform

#  TODO abfrage über SQL-Datenbank nach Städtenamen?

ID = 'Gitter_ID_100m'
x = 'x_mp_100m'
y = 'y_mp_100m'
val = 'Einwohner'

fname = 'Zensus_Bevoelkerung_100m-Gitter.csv'
data_header = pd.read_csv(fname, delimiter=';', header=0, nrows=0)

data = pd.read_csv(fname, delimiter=';', names=list(data_header),
                   nrows=2000, skiprows=1000)

#print(data[x])
path_export = 'output' + os.sep
shp_export = path_export + 'census_ger_100m_grid.shp'
dbf_export = path_export + 'census_ger_100m_grid.dbf'
shx_export = path_export + 'census_ger_100m_grid.shx'

# Remove output shapefile if it already exists
if os.path.exists(shp_export):
    os.remove(shp_export)
    os.remove(dbf_export)
    os.remove(shx_export)
spatialReference = osgeo.osr.SpatialReference() #will create a spatial reference locally to tell the system what the reference will be
spatialReference.ImportFromEPSG(3035) #here we define this reference to be the EPSG code
driver_export = osgeo.ogr.GetDriverByName('ESRI Shapefile') # will select the driver for our shp-file creation.

shapeData = driver_export.CreateDataSource(shp_export) #so there we will store our data
layer = shapeData.CreateLayer('layer', spatialReference, osgeo.ogr.wkbPoint) #this will create a corresponding layer for our data with given spatial information.
layer_defn = layer.GetLayerDefn() # gets parameters of the current shapefile
index = 0
# from http://www.digital-geography.com/csv-to-shp-with-python/


new_field = osgeo.ogr.FieldDefn(val, osgeo.ogr.OFTString) #we will create a new field with the content of our header
layer.CreateField(new_field)

proj_in = Proj(init='epsg:3035')
proj_out = Proj(init='epsg:4326')
i = 0
data_converted = [[0]*len(list(data))]*len(data)

for ID_item, x_item, y_item, val_item in zip(data[ID], data[x], data[y],
                                      data[val]):
    point = osgeo.ogr.Geometry(osgeo.ogr.wkbPoint)
    xy = transform(proj_in, proj_out, x_item, y_item)
    x = xy[0]
    y = xy[1]
    point.AddPoint(x, y)
    feature = osgeo.ogr.Feature(layer_defn)
    feature.SetGeometry(point) #set the coordinates
    feature.SetFID(index)
    index = feature.GetFieldIndex(val)
    feature.SetField(index, str(val))
    layer.CreateFeature(feature)
    data_converted[i] = [ID_item, x, y, val_item]
    i += 1
    print('\rdata left {}'.format(len(data) - i), end='')

data_converted = pd.DataFrame.from_records(data_converted,
                                           columns=list(data_header))

data_converted.to_csv('census_ger_100m_grid.csv', sep=";")

shapeData.Destroy() #lets close the shapefile

