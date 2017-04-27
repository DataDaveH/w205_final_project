# 
# extract_data.py
# Provides functions to download data from various sources and insert into database
# 
# 

import requests
import datetime
import json
import psycopg2
import pandas as pd
from sqlalchemy import create_engine

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
# Helper Functions
#############################################################################
def isNewer(strDate1, strDate2):
    """Simple utility function for comparing a particular string date format
    strDate1 and strDate2 are date strings in 'YYYY-MM' format
    returns True if strDate2 is newer than strDate1, False otherwise
    NOTE: interprets empty string as "Beginning of time" meaning:
        if strDate1 is empty, returns True
        if strDate1 is not empty but strDate2 IS empty, return False"""
    if len(strDate1) == 0:
        return True
    elif len(strDate2) == 0:
        return False
    else:
        return (int(strDate2[0:4]) > int(strDate1[0:4]) or \
               (int(strDate2[0:4]) == int(strDate1[0:4]) and int(strDate2[-2:]) > int(strDate1[-2:])))


#############################################################################
# Data Extract Functions
#############################################################################

def extract_data_SODA( dict_db_connect, url, table_name, 
                    truncate_table = False, last_update_field = "", last_update_value =  ""):
    """Extracts all data since last_update_value (if provided) from table_name 
    at url using the SODA API""" 
    try:
        # Start runtime
        start_time = datetime.datetime.now()
        print("Starting data extract for data source (" + table_name + ") at time (" + str(start_time) + ").")
        
        # Connect to database
        conn = psycopg2.connect( database = dict_db_connect["database"], 
                                 user = dict_db_connect["user"],
                                 password = dict_db_connect["password"],
                                 host = dict_db_connect["host"],
                                 port = dict_db_connect["port"])
        cur = conn.cursor()
        
        request = url
        chunk_size = 50000
        
        if request[-1] != '?': request += '?'

        # Note: we have to chunk the transfer into blocks of 50000 rows                
        request += "$limit=" + str(chunk_size)
        
        # order results by last_update_field
        if len(last_update_field) > 0:
            request += "&$order=" + last_update_field
        
        # get only the rows since the last data load (if options permit)
        if not truncate_table and len(last_update_field) > 0 and len(last_update_value) > 0:
            # get latest values
            # NOTE: last_update_value must be wrapped in quotes or it is seen as an int
            request += "&$where=" + last_update_field + ">\'" + last_update_value + "'"
            print "Starting last_update_field = " + last_update_field
            print "Starting last_update_value = " + str(last_update_value)

        if truncate_table:
            # truncate the table before insertion
            cur.execute("TRUNCATE TABLE " + table_name + ";")
            print("Truncated data table.")
        
        # loop until all data is received
        offset = 0
        all_data_loaded = False
        #counter = 0
        while not all_data_loaded:
            requestFull = request + "&$offset=" + str(offset)
            #print(requestFull)
            response = requests.get(requestFull, verify=False)
            data = response.json()
            if response.status_code != 200:
                print("Error: Did not complete call to API (status code: " + str(response.status_code) + ")")
                print("Check API call: " + request)
                print(data)
                return False

            # Write each row to data table
            for row in data:
                try:
                    values = ""
                    columns = ""
                    for i in row:
                        columns += '"' + str(i) + '",'
                        
                        if isinstance(row[i],dict):
                            values += "'" + str(row[i]).replace("'","").replace("\\","") + "',"
                        else:
                            values += "'" + str(row[i].encode('ascii','ignore').replace("'","").replace("\\","")) + "',"
                            
                    columns = columns[:-1]
                    values = values[:-1]
                    #counter += 1
                    #print(counter, end=" ")
                    #print("INSERT INTO " + table_name + " (" + columns + ") VALUES (" + values + ");");
                    cur.execute("INSERT INTO " + table_name + " (" + columns + ") VALUES (" + values + ");");
                    conn.commit()
                except Exception as e:
                    # placeholder - sometimes there are weird characters that the db won't take
                    # MUST SORT THIS OUT RATHER THAN SKIPPING THEM!
                    print "exception encountered:\n" +  str(e)
                    return False
            
            print "Added " + str(len(data)) + " records at time (" + str(start_time) + ")."

            # determine if there is more data
            if len(data) == chunk_size:
                offset += chunk_size
            else:
                offset += len(data)
                all_data_loaded = True
                        
        # Close connection
        conn.close()
        
        print ("Loaded " + str(offset) + " records to data source (" + table_name + ").")
        print ("Ended data extract for data source (" + table_name + ") at time (" + 
                str(datetime.datetime.now()) + ").")
    
        # if doing incremental updates, save last value inserted, if there is one
        if len(data) > 0 and not truncate_table and len(last_update_field) > 0:
            last_update_value = row[last_update_field]
            print "Ending last_update_field = " + str(last_update_field)
            print "Ending last_update_value = " + str(last_update_value)
            
    except Exception as inst:
        print(inst.args)
        print(inst)
        return False
    
    # if doing incremental updates, return last value inserted to use next time
    if not truncate_table and len(last_update_field) > 0:
        return str(last_update_value)
    else:
        return True
            

def extract_data_Zillow( dict_db_connect, url, table_name,
                      truncate_table = False, last_update_value =  ""):
    """return True if no errors and no new data to load
    return the newest date string that was loaded into the DB to be stored for next time
    return False if errors occurred"""

    print "Loading Zillow data from (" + url + ")"
    
    if truncate_table:
        last_update_value = ""
    
    try:
        # Read the CSV from the url directly into a pandas dataframe
        df = pd.read_csv(url)
        
        # check if there is newer data
        newDate = list(df.columns.values)[len(df.columns)-1]
        if not isNewer( last_update_value, newDate):
            print "No new data"
            return True
        
        # Drop all rows that aren't for Austin metro area (used instead of Austin city for robustness)
        df = df.drop(df[df.Metro != "Austin"].index)
        
        #Drop all rows that aren't for Texas (since there's Austins outside TX)
        df = df.drop(df[df.State != "TX"].index)
        
        #Get the Last Column's column number
        last_col_index = len(df.columns)-1
        
        #Create a new dataframe with the columns we need for reporting
        df_transformed = pd.DataFrame({'zip_code':[],'city':[],'state':[],'metro':[],'value':[],'date':[]})
        zip_code = list(df.columns.values)[1]
        city = list(df.columns.values)[2]
        state = list(df.columns.values)[3]
        metro = list(df.columns.values)[4]
        final_col_list = [zip_code, city, state, metro, 'value', 'date']
        
        #Start at last column and interate to beginning. Index 7 is the first date col in original data
        new_columns = 0
        for i in range(last_col_index,7,-1):
            #The date is the column header in the zillow data, storing it here
            date = list(df.columns.values)[i]
            #These are the columns that will go into the temp dataframe before being loaded into the new dataframe
            temp_col_list = [zip_code,city,state,metro,list(df.columns.values)[i]]

            #Check if the col date is newer than the last stored date
            if isNewer(last_update_value,date) == True:
                new_columns += 1
                
                #Create a temp dataframe made up of only the temp columns
                df_temp = df.filter(temp_col_list, axis = 1)

                #Add a column with the date in it
                df_temp['date'] = list(df.columns.values)[i]

                #Rename the columns to match the full data frame
                df_temp.columns = ['zip_code','city','state','metro','value','date']

                #Drop any N/A values (tends to only happen in early years)
                df_temp.dropna()

                #Append the temp table to the new table_name
                df_transformed = df_transformed.append(df_temp)

        
        print 'loaded: ' + str(new_columns) + (' new date.' if new_columns == 1 else ' new dates.')
        
        # sql alchemy database connection string
        # database://user:password@host:port/databaseName
        dbConnect = 'postgresql://' + dict_db_connect["user"] + ':' + dict_db_connect["password"] + '@' + \
                    dict_db_connect["host"] + ':' + dict_db_connect["port"] + '/' + dict_db_connect["database"]
        engine = create_engine(dbConnect)

        # if we are truncating the table, let SQL Alchemy do it
        if truncate_table:
            if_exists_string = 'replace'
            print "Truncating table."
        else:
            if_exists_string = 'append'
        
        df_transformed.to_sql(table_name, engine, if_exists  = if_exists_string)

        print "Successfully inserted into database."
        
        return newDate

    except Exception as e:
        print("There was an exception while updating the Zillow data:")
        print(e.args)
        print(e)
        return False






