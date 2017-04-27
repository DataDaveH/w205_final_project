import requests
import datetime
import json
import psycopg2
from googlemaps import Client
from eventlet.timeout import Timeout

# CREATE TABLE zip_codes AS (
# SELECT row_number() OVER () AS row_number, 00000 AS zip_code, location 
# FROM (SELECT DISTINCT location AS location FROM racial_profiling_arrests UNION SELECT DISTINCT vl_street_name AS location FROM racial_profiling_citations) loc);

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

def data_extract():
    try:        
        
        # Start runtime
        start_time = datetime.datetime.now()
        print "Starting (zip_code_map) table load at time (" + str(start_time) + ")."
        
        # Connect to database
        conn = psycopg2.connect(database="finalproject",user="postgres",password="pass",host="localhost",port="5432")
        cur = conn.cursor()

        sql = "SELECT location, row_number FROM zip_codes WHERE zip_code = 0;"
        
        cur.execute(sql)        
        data = cur.fetchall()
        
        api_key = ''
        c = Client(key=api_key)
        
        for row in data:
            
            print "ROW: " + str(row)
            
            clean_location = str(row[0].encode('ascii','ignore').replace("'","").replace("\\",""))
            row_number = row[1]

            sql = "UPDATE zip_code_map SET location = '"+clean_location+"' WHERE row_number = "+str(row_number)+";"
            print sql
            cur.execute(sql)              
            conn.commit()

            location = clean_location + ",Austin,TX"
            print location
            print row_number

            zip_code = '0'
            
            try:
                geocode_result = c.geocode(location)
                if len(geocode_result)==0:
                    zip_code = '99999'
                else:
                    for i in xrange(len(geocode_result[0]['address_components'])):
                        if geocode_result[0]['address_components'][i]['types'][0] == 'postal_code':
                            zip_code = geocode_result[0]['address_components'][i]['long_name']
                if len(zip_code) == 5:
                    sql = "UPDATE zip_code_map SET zip_code = "+zip_code+" WHERE row_number = "+str(row_number)+";"
                    print sql
                    cur.execute(sql)              
                    conn.commit()
            except:
                print "couldn't map"                      
    
        # Commit changes to table and close connection
        conn.close()
    
    # Error logging
    except Exception as inst:
        print(inst.args)
        print(inst)

data_extract() 
