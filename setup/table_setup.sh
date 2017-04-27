# Create database
psql -U postgres -c "CREATE DATABASE finalproject;"

# Create zip code map table
psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS zip_code_map;"
psql -U postgres -d finalproject -c "CREATE TABLE zip_code_map (row_number INT, zip_code INT, location TEXT);"
psql -U postgres -d finalproject -c "\copy zip_code_map FROM '~/w205_final_project/setup/zip_code_map.csv' 
WITH CSV HEADER DELIMITER AS E'\t'"

# Create transformation mapping table
psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS transform_map;"
psql -U postgres -d finalproject -c "CREATE TABLE transform_map (source_table TEXT, target_table TEXT, source_field TEXT, 
target_field TEXT, group_by INT, sum_of INT, count_of INT, min_of INT, max_of INT);"
psql -U postgres -d finalproject -c "\copy transform_map FROM '~/w205_final_project/setup/transform_map.csv' 
WITH CSV HEADER DELIMITER AS E'\t'"

# Create data dictionary table
psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS data_dictionary;"
psql -U postgres -d finalproject -c "CREATE TABLE data_dictionary (table_name TEXT, column_name TEXT, data_value TEXT, 
data_value_desc TEXT);"
psql -U postgres -d finalproject -c "\copy data_dictionary FROM '~/w205_final_project/setup/data_dictionary.csv' 
WITH CSV HEADER DELIMITER AS E'\t'"

# Issued Construction Permits
# https://data.austintexas.gov/Permitting/Issued-Construction-Permits/3syk-w9eu
psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS construction_permits;"
psql -U postgres -d finalproject -c "CREATE TABLE construction_permits (permittype TEXT,permit_type_desc TEXT,
permit_number TEXT,permit_class_mapped TEXT,permit_class TEXT,work_class TEXT,condominium TEXT,permit_location TEXT,
description TEXT,tcad_id TEXT,legal_description TEXT,applieddate TEXT,issue_date TEXT,day_issued TEXT,
calendar_year_issued TEXT,fiscal_year_issued TEXT,issued_in_last_30_days TEXT,issue_method TEXT,status_current TEXT,
statusdate TEXT,expiresdate TEXT,completed_date TEXT,total_existing_bldg_sqft TEXT,remodel_repair_sqft TEXT,
total_new_add_sqft TEXT,total_valuation_remodel TEXT,total_job_valuation TEXT,number_of_floors TEXT,housing_units TEXT,
building_valuation TEXT,building_valuation_remodel TEXT,electrical_valuation TEXT,electrical_valuation_remodel TEXT,
mechanical_valuation TEXT,mechanical_valuation_remodel TEXT,plumbing_valuation TEXT,plumbing_valuation_remodel TEXT,
medgas_valuation TEXT,medgas_valuation_remodel TEXT,original_address1 TEXT,original_city TEXT,original_state TEXT,
original_zip TEXT,council_district TEXT,jurisdiction TEXT,link TEXT,project_id TEXT,masterpermitnum TEXT,
latitude TEXT,longitude TEXT,location TEXT,contractor_trade TEXT,contractor_company_name TEXT,contractor_full_name TEXT,
contractor_phone TEXT,contractor_address1 TEXT,contractor_address2 TEXT,contractor_city TEXT,contractor_zip TEXT,
applicant_full_name TEXT,applicant_org TEXT,applicant_phone TEXT,applicant_address1 TEXT,applicant_address2 TEXT,
applicant_city TEXT,applicantzip TEXT);"

psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS construction_permits_aggregate;"
psql -U postgres -d finalproject -c "CREATE TABLE construction_permits_aggregate (date_number INT, zip_code INT,
residential_or_commercial TEXT, permit_type TEXT, work_class TEXT, 
sum_project_valuation DECIMAL(16,2), total_num_permits INT);"


# Restaurant Inspection Scores
# https://data.austintexas.gov/dataset/Restaurant-Inspection-Scores/ecmv-9xxi
psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS restaurant_inspection_scores;"
psql -U postgres -d finalproject -c "CREATE TABLE restaurant_inspection_scores (restaurant_name TEXT,zip_code TEXT,
inspection_date TEXT,score TEXT,address_city TEXT,address_state TEXT,address TEXT,facility_id TEXT,
process_description TEXT,address_address TEXT,address_zip TEXT);" 

psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS restaurant_inspection_scores_aggregate;"
psql -U postgres -d finalproject -c "CREATE TABLE restaurant_inspection_scores_aggregate (date_number INT, 
zip_code INT, sum_score DECIMAL(16,2), total_num_scores INT, min_score INT, max_score INT);"

# Code Complaint Cases
# https://data.austintexas.gov/Government/Austin-Code-Complaint-Cases/6wtj-zbtb
psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS code_complaint_cases;"
psql -U postgres -d finalproject -c "CREATE TABLE code_complaint_cases (case_id TEXT,address TEXT,house_number TEXT,
street_name TEXT,city TEXT,state TEXT,zip_code TEXT,x TEXT,y TEXT,opened_date TEXT,closed_date TEXT,department TEXT,
case_type TEXT,description TEXT,case_contact TEXT,case_manager TEXT,date_updated TEXT,latitude TEXT,longitude TEXT,
location_city TEXT,location TEXT,location_address TEXT,location_zip TEXT,location_state TEXT);" 

psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS code_complaint_cases_aggregate;"
psql -U postgres -d finalproject -c "CREATE TABLE code_complaint_cases_aggregate (date_number INT, zip_code INT, 
complaint_type TEXT, total_num_cases INT);"

# Residential Water Consumption
# https://data.austintexas.gov/Utility/Austin-Water-Residential-Water-Consumption/sxk7-7k6z
psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS residential_water_consumption;"
psql -U postgres -d finalproject -c "CREATE TABLE residential_water_consumption (year_month TEXT,
postal_code TEXT, customer_class TEXT, total_gallons TEXT);"

psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS residential_water_consumption_aggregate;"
psql -U postgres -d finalproject -c "CREATE TABLE residential_water_consumption_aggregate (year_month INT, 
zip_code INT, custom_class TEXT, total_gallons INT);"

# Commercial Water Consumption
# https://data.austintexas.gov/Utility/Austin-Water-Commercial-Water-Consumption/5h9c-wmds
psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS commercial_water_consumption;"
psql -U postgres -d finalproject -c "CREATE TABLE commercial_water_consumption (year_month TEXT,
postal_code TEXT, customer_class TEXT, total_gallons TEXT);"

psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS commercial_water_consumption_aggregate;"
psql -U postgres -d finalproject -c "CREATE TABLE commercial_water_consumption_aggregate (year_month INT, 
zip_code INT, custom_class TEXT, total_gallons INT);"

# Pothole Repair
# https://data.austintexas.gov/Government/Pothole-Repair/fmm2-ytyt
psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS pothole_repair;"
psql -U postgres -d finalproject -c "CREATE TABLE pothole_repair (sr_number TEXT,sr_type_code TEXT,
sr_type_desc TEXT,sr_department_desc TEXT,sr_method_received_desc TEXT,sr_status_desc TEXT,sr_status_date TEXT,
sr_created_date TEXT,sr_updated_date TEXT,sr_closed_date TEXT,sr_location TEXT,sr_location_street_number TEXT,
sr_location_street_name TEXT,sr_location_city TEXT,sr_location_zip_code TEXT,sr_location_county TEXT,
sr_location_x TEXT,sr_location_y TEXT,sr_location_lat TEXT,sr_location_long TEXT,sr_location_lat_long TEXT,
sr_location_council_district TEXT,sr_location_map_page TEXT,sr_location_map_tile TEXT);"

psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS pothole_repair_aggregate;"
psql -U postgres -d finalproject -c "CREATE TABLE pothole_repair_aggregate (created_date_number INT, zip_code INT, 
status_change_date_number INT, status TEXT, total_num_cases INT);"

# Service Alerts
# https://data.texas.gov/dataset/Service-Alerts/avj9-39zb
psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS service_alerts;"
psql -U postgres -d finalproject -c 'CREATE TABLE service_alerts (alert_id TEXT,start TEXT,"end" TEXT,url TEXT,
effect TEXT,header_text TEXT,route_type TEXT,route_id TEXT,trip TEXT,stop_id TEXT,description_text TEXT,cause TEXT,
sup_timestamp TEXT);'

# 2014-2016 Racial Profiling Dataset Citations
# https://data.austintexas.gov/dataset/2014-Racial-Profiling-Dataset-Citations/mw6q-k5gy
# https://data.austintexas.gov/Public-Safety/Racial-Profiling-Dataset-2015-Citations/sc6h-qr9f
# https://data.austintexas.gov/Public-Safety/2016-Racial-Profiling-Dataset-Citations/gcpe-gehi
psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS racial_profiling_citations;"
psql -U postgres -d finalproject -c "CREATE TABLE racial_profiling_citations (citation_number TEXT,
off_from_date TEXT, off_time TEXT, race_origin_code TEXT, case_party_sex TEXT, reason_for_stop TEXT,
race_known TEXT, vl_street_name TEXT, msearch_y_n TEXT, msearch_type TEXT, msearch_found TEXT);"

psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS racial_profiling_citations_aggregate;"
psql -U postgres -d finalproject -c "CREATE TABLE racial_profiling_citations_aggregate (date_number INT, 
zip_code INT, race_origin_code TEXT, case_party_sex TEXT, reason_for_stop TEXT, race_known TEXT, msearch_y_n TEXT, 
msearch_type TEXT, msearch_found TEXT, total_num_cases INT);"

# 2014-2016 Racial Profiling Arrests
# https://data.austintexas.gov/Public-Safety/2014-Racial-Profiling-Dataset-Arrests/rnv4-98ze
# https://data.austintexas.gov/Public-Safety/Racial-Profiling-Dataset-2015-Arrests/vykk-upaj
# https://data.austintexas.gov/Public-Safety/2016-Racial-Profiling-Dataset-Arrests/834s-nvqn
psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS racial_profiling_arrests;"
psql -U postgres -d finalproject -c "CREATE TABLE racial_profiling_arrests (primary_key TEXT,rep_date TEXT,
rep_time TEXT,sex TEXT,age_at_offense TEXT,apd_race_desc TEXT,location TEXT,person_searched_desc TEXT,
reason_for_stop_desc TEXT,search_based_on_desc TEXT,search_disc_desc TEXT,race_known TEXT,x_coordinate TEXT,
y_coordinate TEXT,sector TEXT,local_field1 TEXT);"

psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS racial_profiling_arrests_aggregate;"
psql -U postgres -d finalproject -c "CREATE TABLE racial_profiling_arrests_aggregate (date_number INT,
zip_code INT,sex TEXT,age_at_offense TEXT,apd_race_desc TEXT,reason_for_stop_desc TEXT,
search_based_on_desc TEXT,search_disc_desc TEXT,race_known TEXT, total_num_cases INT);"

#Zillow absolute home value
#http://files.zillowstatic.com/research/public/Zip/Zip_MedianValuePerSqft_AllHomes.csv
psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS \"Zip_MedianValuePerSqft_AllHomes\";"
psql -U postgres -d finalproject -c "CREATE TABLE \"Zip_MedianValuePerSqft_AllHomes\" (index TEXT, city TEXT, date TEXT, metro TEXT, state TEXT, value INT, zip_code INT);"

#Zillow home value per square foot
#http://files.zillowstatic.com/research/public/Zip/Zip_Zhvi_AllHomes.csv
psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS \"Zip_Zhvi_AllHomes\";"
psql -U postgres -d finalproject -c "CREATE TABLE \"Zip_Zhvi_AllHomes\" (index TEXT, city TEXT, date TEXT, metro TEXT, state TEXT, value INT, zip_code INT);"

#Zillow absolute rent
#http://files.zillowstatic.com/research/public/Zip/Zip_Zri_AllHomesPlusMultifamily.csv
psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS \"Zip_Zri_AllHomesPlusMultifamily\";"
psql -U postgres -d finalproject -c "CREATE TABLE \"Zip_Zri_AllHomesPlusMultifamily\" (index TEXT, city TEXT, date TEXT, metro TEXT, state TEXT, value INT, zip_code INT);"

#Zillow rent per sq foot
#http://files.zillowstatic.com/research/public/Zip/Zip_ZriPerSqft_AllHomes.csv
psql -U postgres -d finalproject -c "DROP TABLE IF EXISTS \"Zip_ZriPerSqft_AllHomes\";"
psql -U postgres -d finalproject -c "CREATE TABLE \"Zip_ZriPerSqft_AllHomes\" (index TEXT, city TEXT, date TEXT, metro TEXT, state TEXT, value INT, zip_code INT);"

# make log folder
mkdir -p log

# schedule task to run once a day at 1am and pass in the install directory (pwd)
#    (to unschedule the task, run "crontab -e" and remove the entry for this program.)
#    this script must be run from the main installation folder
(echo "0 1 * * * sh $(pwd)/setup/runApp.sh $(pwd)") | crontab

