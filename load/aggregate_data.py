# 
# aggregate_data.py
# Provides functions to aggregate previously stored data and store into database
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

def aggregate_data_SODA( dict_db_connect, source_table, target_table, truncate_table = False, last_update_field = "", last_update_value =  ""):
    """Loads all data since last_update_value (if provided) from source_table 
    at url using the SODA API""" 
    try:
        # Start runtime
        start_time = datetime.datetime.now()
        print("Starting data aggregation for data source (" + source_table + ") at time (" + str(start_time) + ").")
        
        # Connect to database
        conn = psycopg2.connect( database = dict_db_connect["database"], 
                                 user = dict_db_connect["user"],
                                 password = dict_db_connect["password"],
                                 host = dict_db_connect["host"],
                                 port = dict_db_connect["port"])
        cur = conn.cursor()

        if truncate_table:
            cur.execute("TRUNCATE TABLE " + target_table + ";");
            print("Truncated (" + target_table +") data table.")

        cur.execute("SELECT * FROM transform_map WHERE target_table = '" + target_table + "';")
        data = cur.fetchall()
                
        insert_columns = ""
        select_columns = ""
        group_by = ""
        for row in data:
            try:
                insert_columns += str(row[3]) + ","
                if row[4]==1: select_columns += str(row[2]) + " AS " + str(row[3]) + ","
                if row[5]==1: select_columns += "SUM(" + str(row[2]) + ") AS " + str(row[3]) + ","
                if row[6]==1: select_columns += "COUNT(" + str(row[2]) + ") AS " + str(row[3]) + ","
                if row[7]==1: select_columns += "MIN(" + str(row[2]) + ") AS " + str(row[3]) + ","
                if row[8]==1: select_columns += "MAX(" + str(row[2]) + ") AS " + str(row[3]) + ","
                if row[4]==1: group_by += str(row[2]) + ","
            except Exception as e:
                print "exception encountered:\n" +  str(e)
                return False
        
        select_columns = select_columns[:-1]
        insert_columns = insert_columns[:-1]
        group_by = group_by[:-1]

        sql = "INSERT INTO " + target_table + " ("+ insert_columns + ") SELECT "
        sql += select_columns + " FROM " + source_table

        if not truncate_table and len(last_update_field) > 0 and len(last_update_value) > 0:
            sql += " WHERE " + last_update_field + " > '" + last_update_value + "'"
            print "Starting last_update_field = " + last_update_field
            print "Starting last_update_value = " + str(last_update_value)
        
        sql += " GROUP BY " + group_by + ";"
        
        print "Inserting into (" + target_table +") table..."
        cur.execute(sql)
        print "Insert completed with status message: " + cur.statusmessage
        conn.commit()

        if not truncate_table and len(last_update_field) > 0:
            cur.execute("SELECT MAX("+last_update_field+") FROM " + source_table + ";")
            last_update_value = cur.fetchone()
        
        conn.close()
            
        print ("Ended data aggregation for data source (" + source_table + ") at time (" + 
                str(datetime.datetime.now()) + ").")
    
        # if doing incremental updates, return last value inserted to use next time
        if not truncate_table and len(last_update_field) > 0:
            print "Ending last_update_field = " + last_update_field
            print "Ending last_update_value = " + str(last_update_value[0])
            return str(last_update_value[0])
        else:
            return True

    except Exception as inst:
        print(inst.args)
        print(inst)
        return False
