# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 10:22:33 2017

@author: jpelda
"""

from pyproj import Proj, transform
import pymysql

con = pymysql.connect(host='localhost', user='root',
                             password='wasteheat', db='test')

query = ("SELECT x, y FROM `census_ger` WHERE y = {}").format(2684050)
cur = con.cursor()
#cur.execute(query)
#data = cur.fetchall()
#print(data)
#
##  TODO abfrage über SQL-Datenbank nach Städtenamen?
#
#index = 'Gitter_ID_100m'
#y1 = 51.54128
#x1 = 9.915804
#y2 = 51.54128
#x2 = 9.945415
#y3 = 51.529268
#x3 = 9.915804
#y4 = 51.529268
#x4 = 9.945415
#
#proj_in = Proj(init='epsg:3035')
#proj_out = Proj(init='epsg:4326')
#latlon = []
#for item in data:
#    x1_3035 = item[0]
#    y1_3035 = item[1]
#    xy = transform(proj_in, proj_out, x1_3035, y1_3035)
#    latlon.append([xy[1], xy[0]])

#query = ("ALTER TABLE `census_ger` ADD lon FLOAT(5,3) ")
#cur.execute(query)
print(latlon)

cur.close()
con.close()

