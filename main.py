# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 10:36:21 2018

@author: jpelda
"""

import os
import sys
sys.path.append(os.getcwd() + os.sep + 'class')

from DataIO import DataIO
from Conditioning import Conditioning
from Allocation import Allocation

test_DataIO = DataIO()
test_Conditioning = Conditioning()
test_Allocation = Allocation()


#########################################################################
# C O N D I T I O N I N G

#########
# INPUT
#########
df_geo = test_DataIO.read_from_sqlServer()
df_census = test_DataIO.read_from_sqlServer()


##############
# Conditioning
##############


df_geo['centroid'] = test_Conditioning.get_centroid(df_geo['SHAPE'])
x, y = test_Conditioning.transform_coords(self, x, y, coord_system)

########
# OUTPUT
########


# write df_geo with centroids to db
from DataIO import write_to_sql_Server
write_DataCentroid = wirte_to_sqlServer
# df_geo.to_sql('centroid', engine, if_exists='replace', index=True)
# oder in DataIO?

# Print Graph
# TODO df_geo into Graph


###########################################################################
# A L L O C A T I O N

#########
# INPUT
#########
df_census_auswahl = DATAFRAME-AUS-MySQL_transf_coord.py() # TODO da drin df
# umbenennen
df_inhabitants = allocation

##############
# Allocation
##############


########
# OUTPUT
########

# TODO ## df.to_sql('iPsQm', engine, if_exists='replace', index=True)
# DB MEMPHIS_Output DB-Table name 'Inhabitants'

# df_wastewater.to_sql('iPsqm', engine, if_exists='replace', index=True)
# DB-Table name 'WastewaterflowOUT' im DB MEMPHIS_Output


# df_sewagewater.to_sql  save df to sql "MEMPHIS_Output.sewage_flows"
# as new table

