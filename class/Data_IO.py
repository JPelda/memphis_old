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

class Data_IO:
    def __init__(self, fname_config):
        self.config = cfp.ConfigParser()
        self.config.read(fname_config)
        self.engine = create_engine(self.config['SQL']['db'], echo=False)

        GIS = self.config['SQL_QUERIES']
        self.xMin = float(GIS['xMin'])
        self.yMin = float(GIS['yMin'])
        self.xMax = float(GIS['xMax'])
        self.yMax = float(GIS['yMax'])
        coords = ((self.xMin, self.yMin),
                  (self.xMax, self.yMin),
                  (self.xMax, self.yMax),
                  (self.xMin, self.yMax),
                  (self.xMin, self.yMin))
        #  TODO instead of using self.bbox_f use self.bbox_s.wkt gives str
        coords = [(x, y) for x, y in coords]
        self.bbox = Polygon(coords)
        self.coord_system = GIS['coord_system']

    def write_to_sqlServer(self, table_name, df):

        df.to_sql(table_name, self.engine, if_exists='replace')
        ('Saved Data to {} in db {}'.format(table_name, self.engine))

    def read_from_sqlServer(self, name):
        '''
        Reads SQL-Database into pandas dataframe, which is worked on.
        Input:
            sql_query: name of sql-query in section SQL_QUERIES in config-file
        '''
#        sql = self.config['SQL_QUERIES'][sql_query]
#        sql = ("SELECT ST_ASText(SHAPE), osm_id, name FROM `roads_goettingen` WHERE (MBRContains({}, ST_GeomFromText(ST_ASText(SHAPE))) = 1").format(self.bbox)
        conf = eval(self.config['SQL_QUERIES'][name])

        table = conf['table']
        col = conf['col']
        coord_system = conf['coord_system']
        geo = conf['geo']

        if coord_system == self.coord_system:
            bbox = ("ST_GEOMFROMTEXT("
                    "'POLYGON(({} {},{} {},{} {},{} {},{} {}))')").format(
                    self.xMin, self.yMin, self.xMax, self.yMin, self.xMax,
                    self.yMax, self.xMin, self.yMax, self.xMin, self.yMin)
            if len(geo) is 1:
                sql = ("SELECT {} FROM {} WHERE MBRContains({}, {}) = 1"
                       ).format(', '.join(col), table, bbox, ', '.join(geo))
            else:
                sql = None
                #  TODO something like:
#                sql = ("SELECT {} FROM {} WHERE "
#                  " {} BETWEEN {} = 1"
#                  ).format(', '.join(col), table, geo, min(self.bbox_f), max(self.bbox_f))
        elif coord_system != self.coord_system:
            if len(geo) == 1:
                #  TODO something like in if --> if statement above
                pass
            else:
                bbox_transformed = transform_coords(
                               [list(self.bbox.exterior.coords)],
                               from_coord=self.coord_system,
                               into_coord=coord_system)
                sql = ("SELECT {} FROM {} WHERE {} BETWEEN {} and {} and "
                       "{} BETWEEN {} and {}"
                       ).format(', '.join(col), table, geo[0],
                               min(bbox_transformed[0])[0],
                               max(bbox_transformed[0])[0],
                               geo[1],
                               min(bbox_transformed[0])[1],
                               max(bbox_transformed[0])[1])


        else:
            sql = ("SELECT {} FROM {}").format(', '.join(col), table)

        df = pd.read_sql(sql, self.engine)

        if coord_system == self.coord_system:
            if len(geo) is 1:
                df['geo'] = df[col[0]].map(loads)

        elif coord_system != self.coord_system:
            if len(geo) == 1:
                #  TODO something like in if --> if statement above
                pass
            else:
                geometry = [(x, y) for
                            x, y in zip(df[geo[0]], df[geo[1]])]
                df['len_x'] = len(set([x[0] for x in geometry]))
                df['len_y'] = len(set([y[1] for y in geometry]))
                geometry = transform_coords([geometry],
                                            from_coord=coord_system,
                                            into_coord=self.coord_system)
                df['geo'] = [Point(x, y) for x, y in geometry[0]]

        return df


if __name__ == "__main__":

    import os

    config = os.path.dirname(os.getcwd()) + os.sep +\
            'config' + os.sep + 'test_config.ini'

    Data = Data_IO(config)

    gis = Data.read_from_sqlServer('gis')
    census = Data.read_from_sqlServer('census')


else:
    pass
