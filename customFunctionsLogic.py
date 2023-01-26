"""This file will only exist until we migrate it to the actual real custom function file
We can delete this when done.
Every function in here is a special use case for the fields that require calculations
from previous calculations
"""
import numpy as np
import geopandas

####### FUNC1 Functions
def calculate_fccnew_summary_speedtier(data):
    download_speed = data["fccnew_max_advertised_download_speed"]
    upload_speed = data["fccnew_max_advertised_upload_speed"]
    if download_speed == 0 or upload_speed == 0:
        return 'No Service'
    elif download_speed <= 25 and upload_speed <= 3:
        return 'Less Than 25/3'
    elif download_speed > 25 and upload_speed > 3 and download_speed < 100 and upload_speed < 10:
        return 'Greater Than 25/3'
    elif download_speed >= 100 and upload_speed >= 10:
        return 'Greater Than 100/10'
    else:
        return 'No Service'


def calculate_fccnew_speedtier(data):
    download_speed = data["fccnew_max_advertised_download_speed"]
    upload_speed = data["fccnew_max_advertised_upload_speed"]
    if download_speed == 0 or upload_speed == 0:
        return 'No Service'
    elif download_speed <= 25 and upload_speed <= 3:
        return 'Less Than 25/3'
    elif download_speed > 25 and upload_speed > 3 and download_speed < 100 and upload_speed < 10:
        return 'Greater Than 25/3'
    elif download_speed >= 100 and upload_speed >= 10:
        return 'Greater Than 100/10'
    else:
        return 'No Service'


def calculate_address_persqmeter(data):
    #### Need input geojson here in CRS 3857 or at the very least the geometry in CRS 3857
    input_geojson = """{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[-82.68245188437649,35.541600938788264],[-82.66871897421989,35.54125173858815],[-82.66820399008901,35.54648958194431],[-82.68279520713041,35.546594335321956],[-82.68245188437649,35.541600938788264]]]},
    "properties":{"project_name":"testing-census","_date":1674579600000,"globalid":"{67D71F9F-ED4D-4D13-8356-C2841FE6FBD3}","objectid":18}}"""
    input_data = geopandas.read_file(input_geojson)
    input_data = input_data.to_crs('3857')
    area = input_data.area # what units is this in???
    address_count = data['address_count']
    return (address_count / area)

def calculate_percent_addresses(data):
    state_survey_count = data['state_survey_count']
    address_count = data['address_count']
    return (float(state_survey_count)/float(address_count) * 100 )

def calculate_adress_rank(data):
    return 123456789

def calculate_fccnew_techquestionable(data):
    return 987654321

def calculate_fccnew_need_more_ook(data):
    return 123456789

def calculate_fccnew_need_survey(data):
    return 987654321

def calculate_fccnew_speed_questionable(data):
    return 123456789

def calculate_fccold_techquestionable(data):
    return 987654321

def calculate_fccold_need_more_ook(data):
    return 123456789

def calculate_fccold_need_survey(data):
    return 987654321

def calculate_fccold_speed_questionable(data):
    return 123456789


###### FUNC2 Functions
def calculate_fccnew_questionable(data):
    return 987654321

def calculate_fccold_questionable(data):
    return 123456789