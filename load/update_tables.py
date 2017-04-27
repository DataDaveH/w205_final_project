# 
# update_tables.py
# Parses config file to load all data and build updated aggregates
# config file must be local and named 'config.ini'
# 

import ConfigParser as cp
import sys
from extract_data import *
from aggregate_data import *
from custom_map_data import *

# config file strings
CONFIG_FILE_NAME = 'config.ini'
DATASOURCE_SECTION = 'DATASOURCE'
AGGREGATE_SECTION = 'AGGREGATE'
CUSTOM_SECTION = 'CUSTOM'
URL_KEY = 'url'
TABLE_NAME_KEY= 'table_name'
LAST_UPDATE_COL_KEY = 'last_update_col'
LAST_UPDATE_VAL_KEY = 'last_update_val'
TYPE_KEY = 'type'
TRUNCATE_KEY = 'truncate'
SOURCE_TABLE_KEY = 'source_table'
TARGET_TABLE_KEY = 'target_table'
CUSTOM_MAP_KEY = 'custom_map_col'

config = cp.ConfigParser()

# this line keeps the config parser from converting option names to lowercase
config.optionxform = str

try:
    if len(config.read(CONFIG_FILE_NAME)) == 0:
        print "Cannot read config file"
        sys.exit("Cannot read config file: " + CONFIG_FILE_NAME)
except Exception as e:
    print "Cannot read config file"
    sys.exit("Cannot read config file:\n" + str(e))

# as of now, database info is hardcoded
# eventually, this should be externally configurable
dict_db_connect = { "database" : "finalproject",
                    "user" : "postgres",
                    "password" : "pass",
                    "host" : "localhost",
                    "port" : "5432"}

# semi-crude but very simple way to validate DATASOURCE config file sections
# first pass verifies there is enough info, on success, second pass loads data
no_errors = True
config_ok = True
for i in range(2):
    for s in config.sections():
        if s.startswith(DATASOURCE_SECTION):
            if URL_KEY in config.options(s):
                url_value = config.get(s, URL_KEY)
            else:
                url_value = ""
            
            if TABLE_NAME_KEY in config.options(s):
                table_name_value = config.get(s, TABLE_NAME_KEY)
            else:
                table_name_value = ""
            
            if LAST_UPDATE_COL_KEY in config.options(s):
                last_update_col_value = config.get(s, LAST_UPDATE_COL_KEY)
            else:
                last_update_col_value = ""
            
            if LAST_UPDATE_VAL_KEY in config.options(s):
                last_update_val_value = config.get(s, LAST_UPDATE_VAL_KEY)
            else:
                last_update_val_value = ""
            
            if TYPE_KEY in config.options(s):
                type_value = config.get(s, TYPE_KEY)
            else:
                type_value = ""
            
            if TRUNCATE_KEY in config.options(s):
                truncate_value = True if config.get(s, TRUNCATE_KEY)[0].lower() == 't' else False
            else:
                truncate_value = False
            
            # at a minimum, we need table name, url, and type
            # if any are missing, error out so it can be fixed
            if len(table_name_value) == 0 or len(url_value) == 0 or len(type_value) == 0:
                print("Config file error:")            
                print("In " + s + "table_name, url, and type are required")
                config_ok = False
                
            # everything is read in for this source, on verify pass, extract the data
            if i == 1:
                if type_value == "SODA":
                    ret = extract_data_SODA( dict_db_connect, url_value, table_name_value, 
                                          truncate_value, last_update_col_value, last_update_val_value)
                    
                    #check ret - it will be either a boolean or a string
                    # here is where we'd write back to the config file if we are not truncating
                    # and storing the last_update_val
                    if isinstance(ret, bool):
                        if ret == False:
                            no_errors = False
                    else:
                        config.set(s, LAST_UPDATE_VAL_KEY, ret)
                        with open(CONFIG_FILE_NAME, 'w') as configfile:
                            config.write(configfile)
                        
                    print ""
                    
                elif type_value == "ZILLOW":
                    ret = extract_data_Zillow( dict_db_connect, url_value, table_name_value,
                                            truncate_value, last_update_val_value)
                    
                    # check ret - it will be either a boolean or a string
                    # write back to the config file if we are not truncating
                    # and storing the last_update_val
                    #print(str(ret))
                    if isinstance(ret, bool):
                        if ret == False:
                            no_errors = False
                    else:
                        config.set(s, LAST_UPDATE_VAL_KEY, ret)
                        with open(CONFIG_FILE_NAME, 'w') as configfile:
                            config.write(configfile)
                    
                    print ""
                                
                else:
                    # unknown type - don't error out, just skip
                    # this could be a convenient way to add sources that aren't quite ready yet to the config
                    print("Unknown source type: " + type_value + "\nSkipping source at " + url_value)

    if not config_ok:
        sys.exit("Cannot proceed until errors are fixed\nexiting...")

print ""

# Do not run custom if errors occurred previously
if no_errors:
    
    # run custom
    try:
        # parse CUSTOM section of config file and call each function            
        for i in range(2):
            for s in config.sections():
                if s.startswith(CUSTOM_SECTION):
                                        
                    if SOURCE_TABLE_KEY in config.options(s):
                        source_table = config.get(s, SOURCE_TABLE_KEY)
                    else:
                        source_table = ""

                    if TARGET_TABLE_KEY in config.options(s):
                        target_table = config.get(s, TARGET_TABLE_KEY)
                    else:
                        target_table = ""
                        
                    if TYPE_KEY in config.options(s):
                        type_value = config.get(s, TYPE_KEY)
                    else:
                        type_value = ""

                    if CUSTOM_MAP_KEY in config.options(s):
                        custom_map_col = config.get(s, CUSTOM_MAP_KEY)
                    else:
                        custom_map_col = ""
                        
                    # at a minimum, we need source table name, target table name, and type
                    # if any are missing, error out so it can be fixed
                    if len(source_table) == 0 or len(target_table) == 0 or len(type_value) == 0 or len(custom_map_col) == 0:
                        print("Config file error:")            
                        print("In " + s + "source_table, target_table, type, and custom_map_col are required")
                        config_ok = False            

                    # everything is read in for this source, on verify pass, load the data
                    if i == 1:
                        if type_value == "SODA":
                            ret = zip_code_map_SODA(dict_db_connect, source_table, target_table, custom_map_col)

                            #check ret - it will be either a boolean or a string
                            # here is where we'd write back to the config file if we are not truncating
                            # and storing the last_update_val
                            if isinstance(ret, bool):
                                if ret == False:
                                    no_errors = False                     
                         
                        print ""

    except Exception as e:
            print(e)
            
# Do not run aggregations if error occurred during extract
if no_errors:
    
    # run aggregations
    try:
        # parse AGGREGATES section of config file and call each function            
        for i in range(2):
            for s in config.sections():
                if s.startswith(AGGREGATE_SECTION):
                                        
                    if SOURCE_TABLE_KEY in config.options(s):
                        source_table = config.get(s, SOURCE_TABLE_KEY)
                    else:
                        source_table = ""

                    if TARGET_TABLE_KEY in config.options(s):
                        target_table = config.get(s, TARGET_TABLE_KEY)
                    else:
                        target_table = ""
                        
                    if LAST_UPDATE_COL_KEY in config.options(s):
                        last_update_col_value = config.get(s, LAST_UPDATE_COL_KEY)
                    else:
                        last_update_col_value = ""

                    if LAST_UPDATE_VAL_KEY in config.options(s):
                        last_update_val_value = config.get(s, LAST_UPDATE_VAL_KEY)
                    else:
                        last_update_val_value = ""

                    if TYPE_KEY in config.options(s):
                        type_value = config.get(s, TYPE_KEY)
                    else:
                        type_value = ""

                    if TRUNCATE_KEY in config.options(s):
                        truncate_value = True if config.get(s, TRUNCATE_KEY)[0].lower() == 't' else False
                    else:
                        truncate_value = False

                    # at a minimum, we need source table name, target table name, and type
                    # if any are missing, error out so it can be fixed
                    if len(source_table) == 0 or len(target_table) == 0 or len(type_value) == 0:
                        print("Config file error:")            
                        print("In " + s + " source_table, target_table, and type are required")
                        config_ok = False            

                    # everything is read in for this source, on verify pass, load the data
                    if i == 1:
                        if type_value == "SODA":
                            ret = aggregate_data_SODA(dict_db_connect, source_table, target_table, 
                                                  truncate_value, last_update_col_value, last_update_val_value)

                            #check ret - it will be either a boolean or a string
                            # here is where we'd write back to the config file if we are not truncating
                            # and storing the last_update_val
                            if isinstance(ret, bool):
                                if ret == False:
                                    no_errors = False
                            else:
                                config.set(s, LAST_UPDATE_VAL_KEY, ret)
                                with open(CONFIG_FILE_NAME, 'w') as configfile:
                                    config.write(configfile)                        
                         
                        print ""

    except Exception as e:
            print(e)

