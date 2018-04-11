# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 10:40:53 2018

@author: jpelda
"""

import os
import sys
sys.path.append(os.path.dirname(os.getcwd()) + os.sep + 'func')
import configparser as cfp
import pandas as pd
from shapely.geometry import Point, LineString, Polygon
from shapely.wkt import loads
from sqlalchemy import create_engine
from transform_coordinates import transform_coords
from osgeo import ogr

class Data_IO:
    '''Access to all sql queries. Initialised by config.ini.
    
    fname_config: str, the config filename
    '''
    def __init__(self, fname_config):
        print('Load config from {}'.format(fname_config))
        self.config = cfp.ConfigParser()
        self.config.read(fname_config)
        self.engine = create_engine(self.config['SQL']['db'], echo=False)

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


    def write_to_sqlServer(self, table_name, df):

        df.to_sql(table_name, self.engine, if_exists='replace')
        ('Saved Data to {} in db {}'.format(table_name, self.engine))

    def read_from_sqlServer(self, name):
        '''Reads SQL-Database into pandas dataframe, which is worked on.
        
        Args:
            sql_query: str, name of sql-query in section SQL_QUERIES
                        in config-file
        
        Returns:
            pandas.DataFrame(sql-db)
        '''

        conf = eval(self.config['SQL_QUERIES'][name])
        table = conf['table']
        col = conf['col']
        coord_system = conf['coord_system']


        if coord_system == self.coord_system:
            bbox = self.bbox

        elif coord_system != self.coord_system:
            bbox = transform_coords([self.bbox],
                                    from_coord=self.coord_system,
                                    into_coord=coord_system)[0]

        if len(col['geo']) is 1:
            sql = self.select_from_where_mbrContains(col, table, bbox)
        elif len(col['geo']) is 2:
            sql = self.select_from_where_between(col, table, bbox)

        else:
            sql = self.__select_from(col, table)

        df = pd.read_sql(sql, self.engine)

        if coord_system == self.coord_system:
            if len(col['geo']) is 1:
                #  TODO find lgenth of x and y values
                df['geo'] = df[col['geo'][0]].map(loads)
            else:
                pass

        elif coord_system != self.coord_system:
            if len(col['geo']) == 1:
                #  TODO find length of x and y values
                df['geo'] = transform_coords([df[col['geo'][0]].map(loads)],
                                             from_coord=coord_system,
                                             into_coord=self.coord_system)
            elif len(col['geo']) == 2:
                df['len_x'] = len(set(df[col['geo'][0]]))
                df['len_y'] = len(set(df[col['geo'][1]]))
                geometry = transform_coords(
                        [Point(x, y) for x, y in zip(
                                df[col['geo'][0]],
                                df[col['geo'][1]])],
                        from_coord=coord_system,
                        into_coord=self.coord_system)
                df['geo'] = geometry

        return df

    def select_from_where_between(self, col, table, bbox):
        sql = ("SELECT {} FROM {} WHERE {} BETWEEN {} and {} and "
               "{} BETWEEN {} and {}").format(
                       ', '.join(self.dict_of_nested_lists_to_list(col)),
                       table, col['geo'][0],
                       min(bbox.exterior.coords.xy[0]),
                       max(bbox.exterior.coords.xy[0]),
                       col['geo'][1],
                       min(bbox.exterior.coords.xy[1]),
                       max(bbox.exterior.coords.xy[1]))
        return sql

    def select_from_where_mbrContains(self, col, table, bbox):
        sql = ("SELECT {} FROM {} WHERE MBRContains({}, ST_GEOMFROMTEXT({})) = 1"
               ).format(', '.join(self.dict_of_nested_lists_to_list(col)),
                        table, self.st_geofromtext_geometry(bbox),
                        ', '.join(col['geo']))
        return sql

    def st_geofromtext_geometry(self, geometry):
        geom = ogr.CreateGeometryFromWkb(geometry.wkb)
        return ("ST_GEOMFROMTEXT('{}')").format(geom)

    def select_from(self, col, table):
        sql = ("SELECT {} FROM {}").format(
                ', '.join(self.dict_of_nested_lists_to_list(col)), table)
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
