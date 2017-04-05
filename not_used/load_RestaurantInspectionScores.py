import load_data_code
import datetime

table_name = "restaurant_inspection_scores"
initial_start_date = datetime.datetime(2014, 3, 1,hour=19) # Start date for initial load; initial load runtime ~1 minute
end_date = datetime.datetime(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day,hour=19)-\
    datetime.timedelta(days=1) # End time is yesterday
date_format = "isoformat()" # Format date for API call
api_url = "https://data.austintexas.gov/resource/nguv-n54k.json?$limit=50000&inspection_date="
load_data_code.data_extract(table_name,initial_start_date,end_date,date_format,api_url)
