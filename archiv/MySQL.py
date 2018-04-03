# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 12:54:19 2018

@author: jpelda
"""
from datetime import date, datetime, timedelta
#import mysql.connector
#from mysql.connector import errorcode
from sqlalchemy import create_engine
import pymysql
import pandas as pd

#DB_TYPE = 'Mariadb'
#DB_DRIVER = 'mysqld'
#DB_USER = 'root'
#DB_PASS = 'wasteheat'
#DB_HOST = 'localhost'
#DB_PORT = '3306'
#DB_NAME = 'MEMPHIS'
#DB_POOL_SIZE = 50
#DB_TABLE_NAME = 'census_ger'
#
#SQLALCHEMY_DATABASE_URI = '%s+%s://%s:%s@%s:%s/%s' % (
#        DB_TYPE, DB_DRIVER, DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME)
#ENGINE = create_engine(SQLALCHEMY_DATABASE_URI,
#                       pool_size=DB_POOL_SIZE,
#                       max_overflow=0)
#print(ENGINE)

cnx = pymysql.connect(host='localhost', user='root',
                             password='wasteheat', db='test')
cursor = cnx.cursor()
#query = ("SELECT ich, du FROM census_ger")
#val = 4
#cursor.execute(query, (val))
#
#for (ich, du) in cursor:
#    print("ich {}, du {}".format(ich, du))


DB_NAME = 'MEMPHIS'

TABLES = {}
#TABLES['employees'] = (
#    "CREATE TABLE `employees` ("
#    "  `emp_no` int(11) NOT NULL AUTO_INCREMENT,"
#    "  `birth_date` date NOT NULL,"
#    "  `first_name` varchar(14) NOT NULL,"
#    "  `last_name` varchar(16) NOT NULL,"
#    "  `gender` enum('M','F') NOT NULL,"
#    "  `hire_date` date NOT NULL,"
#    "  PRIMARY KEY (`emp_no`)"
#    ") ENGINE=InnoDB")
#TABLES['departments'] = (
#    "CREATE TABLE `departments` ("
#    "  `dept_no` char(4) NOT NULL,"
#    "  `dept_name` varchar(40) NOT NULL,"
#    "  PRIMARY KEY (`dept_no`), UNIQUE KEY `dept_name` (`dept_name`)"
#    ") ENGINE=InnoDB")
TABLES['salaries'] = (
    "CREATE TABLE `salaries` ("
    "  `emp_no` int(11) NOT NULL,"
    "  `salary` int(11) NOT NULL,"
    "  `from_date` date NOT NULL,"
    "  `to_date` date NOT NULL,"
    "  PRIMARY KEY (`emp_no`,`from_date`), KEY `emp_no` (`emp_no`),"
    "  CONSTRAINT `salaries_ibfk_1` FOREIGN KEY (`emp_no`) "
    "     REFERENCES `employees` (`emp_no`) ON DELETE CASCADE"
    ") ENGINE=InnoDB")
TABLES['census_ger'] = (
        "CREATE TABLE `census_ger` ("
        "  `grid_ID_100m` varchar(20) NOT NULL,"
        "  `x_mp_100m` int(8) NOT NULL,"
        "  `y_mp_100m` int(8) NOT NULL,"
        "  `inhabitans` int(5) NOT NULL,"
        "  PRIMARY KEY (`x_mp_100m`,`y_mp_100m`), UNIQUE KEY `grid_ID_100m` "
        "  (`grid_ID_100m`) "
        ") ENGINE=MyISAM")
TABLES['roads_ns'] = (
        "CREATE TABLE `roads_ns` ("
        "  `osm_id` int(15),"
        "  `code` int(6),"
        "  `fclass` text,"
        "  `name` text,"
        "  `ref` varchar(20),"
        "  `oneway` char(5),"
        "  `maxspeed` int(3),"
        "  `layer` int(2),"
        "  `bridge` char(2),"
        "  `tunnel` char(2),"
        "  UNIQUE KEY `osm_id` "
        "  (`osm_id`) "
        ") ENGINE=MyISAM")

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

try:
    cnx.database = DB_NAME
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)

for name, ddl in TABLES.items():
    try:
        print("Creating table {}: ".format(name), end='')
        cursor.execute(ddl)
    except pymysql.Error as err:
            print(err)
    else:
        print("OK")

add_employee = ("INSERT INTO employees "
               "(first_name, last_name, hire_date, gender, birth_date) "
               "VALUES (%s, %s, %s, %s, %s)")
add_salary = ("INSERT INTO salaries "
              "(emp_no, salary, from_date, to_date) "
              "VALUES (%(emp_no)s, %(salary)s, %(from_date)s, %(to_date)s)")
add_census_ger = ("INSERT INTO census_ger "
                  "(grid_ID_100m, x_mp_100m, y_mp_100m, inhabitans) "
                  "VALUES (%s, %s, %s, %s)")

tomorrow = datetime.now().date() + timedelta(days=1)
data_employee = ('Geert', 'Vanderkelen', tomorrow, 'M', date(1977, 6, 14))

# Insert new employee
cursor.execute(add_employee, data_employee)
emp_no = cursor.lastrowid
# Insert salary information
data_salary = {
  'emp_no': emp_no,
  'salary': 50000,
  'from_date': tomorrow,
  'to_date': date(9999, 1, 1),
}
cursor.execute(add_salary, data_salary)



#index = 'Gitter_ID_100m'
#x = 'x_mp_100m'
#y = 'y_mp_100m'
#val = 'Einwohner'
#
#fname = 'Zensus_Bevoelkerung_100m-Gitter.csv'
#data = pd.read_csv(fname, delimiter=';', header=0, nrows=20)
#i = 0
#data = data.to_records()
#print(data)
#data = [('hello', 1, 1, 2)]
#try:
##    for grid, x, y, inhab in zip(data['Gitter_ID_100m'], data['x_mp_100m'],
##                                 data['y_mp_100m'], data['Einwohner']):
##    data_census_ger = tuple(data['Gitter_ID_100m'], data['x_mp_100m'],
##                                 data['y_mp_100m'], data['Einwohner'])
##        data_census_ger = (grid, x, y, inhab)
#    #    print(data_census_ger)
##        cursor.executemany(add_census_ger, data_census_ger)
#    cursor.executemany(add_census_ger, data)
##        print('\rdata left {}'.format(len(data) - i), end='')
##        i += 1
#except Exception as err:
#    cursor.execute("DELETE FROM census_ger")
#    print(err.msg)

# Make sure data is committed to the database
cnx.commit()
cursor.close()
cnx.close()
