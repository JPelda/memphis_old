# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 17:38:35 2017

@author: afischea
"""

#import ladedb as ldb
#
#data = ldb.importData(filename.db)
#print(data['lon'])

#import os, sys, sqlite3
#import os, sqlite3
#
#if not os.path.exists("./OSMData.db"):
#  print("Datenbank OSMdata.db nicht vorhanden.")
#


        
#connection = sqlite3.connect("./OSMDataa.db")
#cursor = connection.cursor()

#if connection.is_connected():
#        print("Connected to OSM database")


#def userOSM_db_auslesen():
#    global OSMid, OSMdata 
#    
#    connection = sqlite3.connect("./OSMData.db")
#    cursor = connection.cursor()
#    sql = "SELECT * FROM node"
#    cursor.execute(sql)
#    for dsatz in cursor:
#        OSMid = dsatz[0]
#        OSMdata = dsatz[1]
#       
#    connection.close()
#    return ()
#
#
#
#
#
#def get_posts():
#    with connection:
#        cursor.execute("SELECT * FROM node")
#        print(cursor.fetchall())
#


import sqlite3
connection = sqlite3.connect("./OSMData.db")

cursor = connection.cursor()


#    
##eine Zeile ausgeben lassen
#cursor.execute("SELECT * FROM node") 
#print("\nfetch one:")
#res = cursor.fetchone() 
#print(res)
#
#

#komplette Tabelle anzeigen lassen
cursor.execute("SELECT * FROM node") 
print("fetchall:")
result = cursor.fetchall() 
for r in result:
    print(r)

cursor.execute("SELECT * FROM relation") 
print("fetchall:")
result = cursor.fetchall() 
for r in result:
    print(r)



cursor.execute("SELECT * FROM way") 
print("fetchall:")
result = cursor.fetchall() 
for r in result:
    print(r)


##eine Zeile ausgeben lassen
#cursor.execute("SELECT * FROM node") 
#print("\nfetch one:")
#res = cursor.fetchone() 
#print(res)