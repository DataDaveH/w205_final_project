# 
# aggregates.py
# Provides functions to download data from various sources and insert into database
# 
# 

import requests
import datetime
import json
import psycopg2
import pandas as pd

# Will hide urrlib3 warnings for the purposes of this project.
# Currently receiving this error message because an older version of Python is loaded to AMI.
# InsecurePlatformWarning /usr/lib/python2.7/site-packages/requests-2.10.0-py2.7.egg/requests/
# packages/urllib3/connectionpool.py:821: InsecureRequestWarning: Unverified HTTPS request is 
# being made. Adding certificate verification is strongly advised. 
# See: https://urllib3.readthedocs.org/en/latest/security.html 
# InsecureRequestWarning: Unverified HTTPS request is being made. Adding certificate verification 
# is strongly advised. See: https://urllib3.readthedocs.org/en/latest/security.html
# SNIMissingWarning: An HTTPS request has been made, but the SNI (Subject Name Indication) 
# extension to TLS is not available on this platform. This may cause the server to present an 
# incorrect TLS certificate, which can cause validation failures. You can upgrade to a newer 
# version of Python to solve this. For more information, see 
# https://urllib3.readthedocs.org/en/latest/security.html#snimissingwarning.
from requests.packages.urllib3.exceptions import InsecurePlatformWarning
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from requests.packages.urllib3.exceptions import SNIMissingWarning
requests.packages.urllib3.disable_warnings(SNIMissingWarning)


#############################################################################
# Data Aggregate Functions
#############################################################################

def zip_code_map_SODA( dict_db_connect, source_table, target_table, custom_map_col):
    """Map all data to zip code values""" 
    try:
        # Start runtime
        start_time = datetime.datetime.now()
        print("Starting temp table (" + target_table + ") creation at time (" + str(start_time) + ").")
        
        # Connect to database
        conn = psycopg2.connect( database = dict_db_connect["database"], 
                                 user = dict_db_connect["user"],
                                 password = dict_db_connect["password"],
                                 host = dict_db_connect["host"],
                                 port = dict_db_connect["port"])
        cur = conn.cursor()

        print("Dropping temp table if exists.")
        cur.execute("DROP TABLE IF EXISTS " + target_table + ";")
        
        sql = "CREATE TABLE " + target_table + " AS (SELECT " + source_table
        sql += ".*, COALESCE(zip_code_map.zip_code,99999) AS zip_code FROM " + source_table
        sql += " LEFT JOIN zip_code_map ON zip_code_map.location = " + source_table + "." + custom_map_col + ");"                

        print sql
        cur.execute(sql)
        conn.commit()
        conn.close()
        print "Created temp table with status message: " + cur.statusmessage        
            
        print ("Ended temp table creation for table (" + source_table + ") at time (" + 
                str(datetime.datetime.now()) + ").")
        return True

    except Exception as inst:
        print(inst.args)
        print(inst)
        return False
