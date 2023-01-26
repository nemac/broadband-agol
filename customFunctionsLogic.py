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
    fccold_summary_category = data['fccold_summary_category']
    categories_list_one = ['DSL', 'Satellite']
    categories_list_two = ['Cable', 'Fiber', 'Fixed Wireless']

    if not any(category in fccold_summary_category for category in categories_list_one):
      if any(category in fccold_summary_category for category in categories_list_two):
          return 1 # tech is questionable
      else: 
          return 0 # tech is not questionable
    return 0 # default return 0????

def calculate_fccold_need_more_ook(data):
    # HERE DATA is SUMMARY
    ookola_mobile_total_tests = data['ookola_mobile_total_tests']
    tech_questionable = data['tech_questionable']
    need_ook_speedtest = ookola_mobile_total_tests > 2 or ookola_mobile_total_tests == None
    if need_ook_speedtest:
        ookola_mobile_avg_d_mbps = data['ookola_mobile_avg_d_mbps']
        fccold_all_max_down = data['fccold_all_max_down']
        address_count = data['address_count']
        state_survey_count = data['state_survey_count']
        state_survey_maxdownload = data['state_survey_maxdownload']
        
        
        
        ook_speedtestsless = int(ookola_mobile_total_tests > 1 and ookola_mobile_avg_d_mbps < fccold_all_max_down)
        ncsur_peedtestsless = int(address_count/state_survey_count > .1 and state_survey_maxdownload < fccold_all_max_down)
        return  tech_questionable + ook_speedtestsless + ncsur_peedtestsless
    return 0

def calculate_fccold_need_survey(data):
    '''CONDITION:
        case when need_ncsur = 1 then tech_questionable + ook_speedtestsless + ncsur_peedtestsless else 0 end as need_survey'''
        # ORDER: 2
    '''NEEDED FIELDS:
        tech_quesitonable > calculated
        ook_speedtestsless
        ncsur_peedtestsless'''
    print('fcc_old_need_survey')
    return 987654321

def calculate_fccold_speed_questionable(data):
    '''CONDITION:
        case when (fccold_all_max_down <= 25 AND fccold_all_max_up <= 3 ) or fccold_summary_speedtier like '%No Service%'  then 1 else 0 end speed_questionable,'''
        # ORDER: 1
    '''NEEDED FILES:
        fccold_all_max_down
        fccold_all_max_up
        fccold_summary_speedtier'''
    print('fcc_old_speed_questionable')
    return 123456789


###### FUNC2 Functions
def calculate_fccnew_questionable(data):
    '''CONDITION:
        case when tech_questionable > 0 or fccnew_summary_speedtier like '%No Service%' then speed_questionable + ncsur_speed_questionable + ookola_speed_questionable + tech_questionable + ook_speedtestsless + ncsur_peedtestsless else 0 end as questionable'''
        # ORDER: 3
    '''NEEDED FIEDS:
        OUTER:
        tech_questionable > calculated here
        fccnew_summary_speedtier
        INNER:
        speed_questionable > calculated here
        ncsur_speed_questionable 
        ookola_speed_questionable 
        tech_questionable > calculated here
        ook_speedtestsless
        ncsur_peedtestsless'''
    print('isquestionable')
    return 987654321

def calculate_fccold_questionable(data):
    '''CONDITION: case when tech_questionable > 0  or fccold_summary_speedtier like '%No Service%' then speed_questionable + ncsur_speed_questionable + ookola_speed_questionable + tech_questionable + ook_speedtestsless + ncsur_peedtestsless else 0 end as questionable,'''
        # ORDER: 3
    '''NEEDED FIELDS:
        tech_questionable > calculated
        fccold_summary_speedtier
        speed_questionable > calculated
        ncsur_speed_questionable
        ookola_speed_questionable
        tech_questionable > calculated
        ook_speedtestsless
        ncsur_peedtestsless'''
    print('fcc_old_questionable')
    return 123456789