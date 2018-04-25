# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 10:40:53 2018

@author: jpelda
"""

import os
import sys

import configparser as cfp
import pandas as pd
from shapely.geometry import Point, LineString, Polygon
from shapely.wkt import loads
import shapely.wkb
from sqlalchemy import create_engine
from osgeo import ogr
import time
from sqlalchemy import types
import itertools


sys.path.append(os.path.dirname(os.getcwd()) + os.sep + 'func')
from transform_coordinates import transform_coords


class Data_IO:
    '''Access to all sql queries. Initialised by config.ini.

    fname_config: str, the config filename
    '''
    def __init__(self, fname_config):
        print('Load config from {}'.format(fname_config))
        self.config = cfp.ConfigParser()
        self.config.read(fname_config)
        self.engine = create_engine(self.config['SQL']['db'], echo=False,
                                    encoding='utf-8')

        GIS = self.config['SQL_QUERIES']
        self.xMin = float(GIS['xMin'])
        self.yMin = float(GIS['yMin'])
        self.xMax = float(GIS['xMax'])
        self.yMax = float(GIS['yMax'])
        coords = ((self.xMin, self.yMin),
                  (self.xMin, self.yMax),
                  (self.xMax, self.yMax),
                  (self.xMax, self.yMin),
                  (self.xMin, self.yMin))
        self.bbox = Polygon(coords)
        self.coord_system = GIS['coord_system']

    def write_to_sqlServer(self, table_name, df, dtype={}):
        '''Writes to SQL-Database.

        Args:
            table_name: str, name of table to write to
            df: pandas.DataFrame(), which values are written to table

        Kwargs:
            dtype: dict, {col: type} type is of int, float, or geometry etc.

        Returns:

        '''
        print('Save data to {} in db {}'.format(table_name, self.engine))

        if 'GEOMETRY' in dtype.values():
            name = list(dtype.keys())[list(dtype.values()).index('GEOMETRY')]

            col = [x + ' ' + dtype[x] for x in dtype]
            print(', '.join(col))
            sql_new_table = ("CREATE OR REPLACE TABLE `{}` "
                             "({})COLLATE='utf8_bin'").format(table_name,
                                                              ', '.join(col))
            print(sql_new_table)
            df[name] = ["ST_GEOMFROMTEXT('{}', {})".format(x, 4326) for
                           x in df[name]]

            data = list(df.itertuples(index=False, name=None))
            data = str(data).strip('[]')
            data = data.replace('"', '')

            sql = "INSERT INTO `{}` ({}) VALUES {}".format(
                    table_name, ', '.join(dtype.keys()), data)
            sql_types = "ALTER TABLE `raster_visual` "\
                        "MODIFY COLUMN `{}` GEOMETRY "\
                        .format(name, name)

            conn = self.engine.connect()
            conn.execute(sql_new_table)
            conn.execute(sql)
            conn.close()

        else:
            df.to_sql(table_name, self.engine, if_exists='replace',
                      index=False)

        print("Saved.")

    def read_from_sqlServer(self, name):
        '''Reads SQL-Database into pandas dataframe.

        Args:
            sql_query: str, name of sql-query in section SQL_QUERIES
                        in config-file

        Returns:
            pandas.DataFrame(sql-db)
        '''

        conf = eval(self.config['SQL_QUERIES'][name])
        table = conf['table']
        col = conf['col']

        if 'coord_system' in conf.keys():
            coord_system = conf['coord_system']

            if coord_system == self.coord_system:
                bbox = self.bbox
            elif coord_system != self.coord_system and\
                    coord_system is not None:
                bbox = transform_coords([self.bbox],
                                        from_coord=self.coord_system,
                                        into_coord=coord_system)[0]

        # TODO change import via ST_GEOMFROMTEXT to WKB import.
        # https://www.gaia-gis.it/gaia-sins/spatialite-cookbook/html/wkt-wkb.html
        # Import as string = ST_AsBinary(name)
        # ST_GeomFromWKB(x'01010000008D976E1283C0F33F16FBCBEEC9C30240')
        # shapely.wkb.loads(string)
        if 'SHAPE' in col.keys():
            if len(col['SHAPE']) is 1:
                sql = self.select_from_where_mbrContains(col, table, bbox)

            elif len(col['SHAPE']) is 2:
                sql = self.select_from_where_between(col, table, bbox)
        else:
            sql = self.select_from(col, table)

        df = pd.read_sql(sql, self.engine)

        if 'coord_system' in conf.keys():
            if coord_system == self.coord_system:
                if len(col['SHAPE']) is 1:
                    #  TODO find lgenth of x and y values
                    df['SHAPE'] = df[col['SHAPE'][0]].map(loads)

            elif coord_system != self.coord_system and\
                    coord_system is not None:
                if len(col['SHAPE']) == 1:
                    #  TODO find length of x and y values
                    df['SHAPE'] = transform_coords(
                        [df[col['SHAPE'][0]].map(loads)],
                        from_coord=coord_system,
                        into_coord=self.coord_system)
                elif len(col['SHAPE']) == 2:
                    df['len_x'] = len(set(df[col['SHAPE'][0]]))
                    df['len_y'] = len(set(df[col['SHAPE'][1]]))
                    SHAPEmetry = transform_coords(
                        [Point(x, y) for x, y in zip(
                                df[col['SHAPE'][0]],
                                df[col['SHAPE'][1]])],
                        from_coord=coord_system,
                        into_coord=self.coord_system)
                    df['SHAPE'] = SHAPEmetry
        if 'SHAPE' in df.keys():
            del df[col['SHAPE'][0]]
        return df

    def select_from_where_between(self, col, table, bbox):
        sql = ("SELECT {} FROM {} WHERE {} BETWEEN {} and {} and "
               "{} BETWEEN {} and {}").format(
                       ', '.join(self.dict_of_nested_lists_to_list(col)),
                       table, col['SHAPE'][0],
                       min(bbox.exterior.coords.xy[0]),
                       max(bbox.exterior.coords.xy[0]),
                       col['SHAPE'][1],
                       min(bbox.exterior.coords.xy[1]),
                       max(bbox.exterior.coords.xy[1]))
        return sql

    def select_from_where_mbrContains(self, col, table, bbox):
        sql = ("SELECT {} FROM {} WHERE MBRContains({}, ST_GEOMFROMTEXT({})) = 1"
               ).format(', '.join(self.dict_of_nested_lists_to_list(col)),
                        table, self.st_geofromtext_geometry(bbox),
                        ', '.join(col['SHAPE']))
        return sql

    def st_geofromtext_geometry(self, geometry):
        geom = ogr.CreateGeometryFromWkb(geometry.wkb)
        return ("ST_GEOMFROMTEXT('{}')").format(geom)

    def select_from(self, col, table):
        col = col.values()
        sql = ("SELECT {} FROM {}").format(', '.join([x for x in col if
                                                      x is not None]), table)
        return sql


    def dict_of_nested_lists_to_list(self, dictionary):
        dictionary = [dictionary[x] for x in dictionary.keys()]
        arr = []
        for item in dictionary:
            if type(item) == list:
                for x in item:
                    arr.append(x)
            else:
                if item is '*':
                    arr = [item]
                    break
                else:
                    arr.append(item)
        ret = arr
        return ret

if __name__ == "__main__":

    import os

    config = os.path.dirname(os.getcwd()) + os.sep +\
            'config' + os.sep + 'test_config.ini'

    Data = Data_IO(config)

    gis = Data.read_from_sqlServer('gis')
    census = Data.read_from_sqlServer('census')


else:
    pass
