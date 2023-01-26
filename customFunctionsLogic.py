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

def calculate_fccnew_techquestionable(data):
    fccnew_summary_categories = data['fccnew_summary_categories'] # this comes from 'categories' originally
    categories_list_one = ['copper', 'gso satellite', 'ngso satellite']
    categories_list_two = ['cable, fiber, licensed_fixed_wireless']
    if not any(category in fccnew_summary_categories for category in categories_list_two):
      if any(category in fccnew_summary_categories for category in categories_list_one):
          return 1 # tech is questionable
      else: 
          return 0 # tech is not questionable
    return 0 # default return 0????

def calculate_fccnew_need_more_ook(data):
    # HERE DATA is SUMMARY
    ookola_mobile_total_tests = data['ookola_mobile_total_tests']
    fccnew_max_advertised_download_speed = data['fccnew_max_advertised_download_speed']
    # Is null converted to 0?  SQL uses null comparison for fccnew_max_advertised_download_speed
    need_ook_speedtest = ookola_mobile_total_tests < 2 or fccnew_max_advertised_download_speed is 0
    if need_ook_speedtest:
        tech_questionable = data['fccnew_techquestionable']
        ookola_mobile_avg_d_mbps = data['ookola_mobile_avg_d_mbps']
        address_count = data['address_count']
        state_survey_count = data['state_survey_count']
        state_survey_maxdownload = data['state_survey_maxdownload']
        
        ook_speedtestsless = int(ookola_mobile_total_tests > 1 and ookola_mobile_avg_d_mbps < fccnew_max_advertised_download_speed)
        ncsur_peedtestsless = int(address_count/state_survey_count > .1 and state_survey_maxdownload < fccnew_max_advertised_download_speed)
        return  tech_questionable + ook_speedtestsless + ncsur_peedtestsless
    return 0

def calculate_fccnew_need_survey(data):
    # DATA
    tech_questionable = data['fccnew_techquestionable']
    ookola_mobile_total_tests = data['ookola_mobile_total_tests']
    fccnew_max_advertised_download_speed = data['fccnew_max_advertised_download_speed']
    ookola_mobile_avg_d_mbps = data['ookola_mobile_avg_d_mbps']
    address_count = data['address_count']
    state_survey_count = data['state_survey_count']
    state_survey_maxdownload = data['state_survey_maxdownload']

    # CALCULATIONS
    need_ncsur = 0
    if (address_count/state_survey_count) < .1 or not state_survey_count:
        need_ncsur = 1
    ook_speedtestsless = int(ookola_mobile_total_tests > 1 and ookola_mobile_avg_d_mbps < fccnew_max_advertised_download_speed)
    ncsur_peedtestsless = int(address_count/state_survey_count > .1 and state_survey_maxdownload < fccnew_max_advertised_download_speed)
    return_value = 0
    if need_ncsur:
        return_value = tech_questionable + ook_speedtestsless + ncsur_peedtestsless
    return return_value

def calculate_fccnew_speed_questionable(data):
    fccnew_summary_speedtier = data['fccnew_summary_speedtier']
    no_service = ('No Service' in fccnew_summary_speedtier)
    fccnew_max_advertised_download_speed = data['fccnew_max_advertised_download_speed']
    fccnew_max_advertised_upload_speed = data['fccnew_max_advertised_upload_speed']
    speed_questionable = int((fccnew_max_advertised_download_speed <= 25 and fccnew_max_advertised_upload_speed <= 3 ) or no_service)

    return speed_questionable

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
    # SQL accounts for NULL but I think we are setting to 0?
    need_ook_speedtest = ookola_mobile_total_tests < 2
    if need_ook_speedtest:
        tech_questionable = data['fccold_techquestionable']
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
    fccold_summary_speedtier = data['fccold_summary_speedtier']
    no_service = ('No Service' in fccold_summary_speedtier)
    fccold_all_max_down = data['fccold_all_max_down']
    fccold_all_max_up = data['fccold_all_max_up']
    speed_questionable = int((fccold_all_max_down <= 25 and fccold_all_max_up <= 3 ) or no_service)
    return speed_questionable

###### FUNC2 Functions
def calculate_fccnew_questionable(data):
    tech_questionable = data['fccnew_techquestionable']
    fccnew_summary_speedtier = data['fccnew_summary_speedtier']
    no_service = ('No Service' in fccnew_summary_speedtier)
    if tech_questionable > 0 or no_service:
        
        state_survey_maxdownload = data['state_survey_maxdownload']
        state_survey_maxupload = data['state_survey_maxupload']
        ookola_mobile_avg_d_mbps = data['ookola_mobile_avg_d_mbps']
        ookola_mobile_avg_u_mbps = data['ookola_mobile_avg_u_mbps']
        ookola_mobile_total_tests = data['ookola_mobile_total_tests']
        address_count = data['address_count']
        state_survey_count = data['state_survey_count']

        speed_questionable = data['fccnew_speed_questionable']
        ncsur_speed_questionable = int(state_survey_maxdownload <= 25 and state_survey_maxupload <= 3)
        ookola_speed_questionable = int(ookola_mobile_avg_d_mbps <= 25 and ookola_mobile_avg_u_mbps <= 3)
        ook_speedtestsless = int(ookola_mobile_total_tests > 1 and ookola_mobile_avg_d_mbps < fccnew_max_advertised_download_speed)
        ncsur_peedtestsless = int(address_count/state_survey_count > .1 and state_survey_maxdownload < fccnew_max_advertised_download_speed)

        return speed_questionable + ncsur_speed_questionable + ookola_speed_questionable + tech_questionable + ook_speedtestsless + ncsur_peedtestsless

    return 0

def calculate_fccold_questionable(data):
    tech_questionable = data['fccold_techquestionable']
    fccold_summary_speedtier = data['fccold_summary_speedtier']
    no_service = ('No Service' in fccold_summary_speedtier)
    if tech_questionable > 0 or no_service:
        fccold_all_max_down = data['fccold_all_max_down']
        state_survey_maxdownload = data['state_survey_maxdownload']
        state_survey_maxupload = data['state_survey_maxupload']
        ookola_mobile_avg_d_mbps = data['ookola_mobile_avg_d_mbps']
        ookola_mobile_avg_u_mbps = data['ookola_mobile_avg_u_mbps']
        ookola_mobile_total_tests = data['ookola_mobile_total_tests']
        address_count = data['address_count']
        state_survey_count = data['state_survey_count']

        speed_questionable = data['fccold_speed_questionable']
        ncsur_speed_questionable = int(state_survey_maxdownload <= 25 and state_survey_maxupload <= 3)
        ookola_speed_questionable = int(ookola_mobile_avg_d_mbps <= 25 and ookola_mobile_avg_u_mbps <= 3)
        ook_speedtestsless = int(ookola_mobile_total_tests > 1 and ookola_mobile_avg_d_mbps < fccold_all_max_down)
        ncsur_peedtestsless = int(address_count/state_survey_count > .1 and state_survey_maxdownload < fccold_all_max_down)

        return speed_questionable + ncsur_speed_questionable + ookola_speed_questionable + tech_questionable + ook_speedtestsless + ncsur_peedtestsless
    
    return 0
