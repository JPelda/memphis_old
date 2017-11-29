# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 14:14:55 2017

@author: narand
"""

import osmapi
import numpy as np
import sqlite3
import os.path

def progress(count, total, suffix=''):
    bar_len = 50
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    print(chr(27) + "[2J")
    print('[%s] %s%s %s\r' % (bar, percents, '%', suffix))

#goe:
#min_lon = 9.81
#min_lat = 51.48
#max_lon = 10.03
#max_lat = 51.60

##kleiner teil Goe
#min_lon = 9.9153757095
#min_lat = 51.5468020901
#max_lon = 9.9256753922
#max_lat = 51.555448176
#


min_lon = 9.9446547031
min_lat = 51.5366828822
max_lon = 9.9459850788
max_lat = 51.5373302052

step_lon = 0.01
step_lat = 0.01

dbName = 'OSMData.db'

percent = 0
array_lat = np.arange(min_lat, max_lat, step_lat)
array_lon = np.arange(min_lon, max_lon, step_lon)
length_lat = len(array_lat)
length_lon = len(array_lon)
size = length_lat * length_lon

api = osmapi.OsmApi()

if not os.path.exists(dbName):
    connection = sqlite3.connect(dbName)
    cursor = connection.cursor()
    sql_command = """
    CREATE TABLE node(
    id INTEGER,
    OSMdata TEXT charset utf8);"""
    cursor.execute(sql_command)

    sql_command = """
    CREATE TABLE relation(
    id INTEGER,
    OSMdata TEXT charset utf8);"""
    cursor.execute(sql_command)

    sql_command = """
    CREATE TABLE way(
    id INTEGER,
    OSMdata TEXT charset utf8);"""
    cursor.execute(sql_command)
else:
    connection = sqlite3.connect(dbName)
    cursor = connection.cursor()

for index_lon, lon in enumerate(array_lon):
    for index_lat, lat in enumerate(array_lat):
        osmData = api.Map(lon, lat, lon+step_lon, lat+step_lat)
        for data in osmData:
            # delete unimportant data
            if('uid' in data['data']):
                del(data['data']['uid'])
            if('user' in data['data']):
                del(data['data']['user'])
            if('timestamp' in data['data']):
                del(data['data']['timestamp'])

            if data['type'] == 'node':
                cursor.execute("INSERT INTO node (id, OSMdata) VALUES (?, ?)",
                               (str(data['data']['id']), str(data['data'])))

            if data['type'] == 'relation':
                cursor.execute("INSERT INTO relation (id, OSMdata) VALUES (?, ?)",
                               (str(data['data']['id']), str(data['data'])))

            if data['type'] == 'way':
                cursor.execute("INSERT INTO way (id, OSMdata) VALUES (?, ?)",
                               (str(data['data']['id']), str(data['data'])))

        progress((index_lon*length_lat+index_lat+1), size)
    connection.commit()

connection.commit()

connection.close()
