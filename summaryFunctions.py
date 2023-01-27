import numpy as np
import json

"""This file will only exist until we migrate it to the actual real custom function file
We can delete this when done.
Every function in here is a special use case for the fields that require calculations
from previous calculations
"""
import numpy as np
import geopandas

def calculate_fccnew_summary_speedtier(data, geometry = None):
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


def calculate_fccnew_speedtier(data, geometry = None):
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


def calculate_address_persqmeter(data, geometry):
    area = geometry.area # what units is this in???
    area = area.values[0]
    address_count = data['address_count']
    return (address_count / area)

def calculate_percent_addresses(data, geometry = None):
    state_survey_count = data['state_survey_count']
    address_count = data['address_count']
    return (float(state_survey_count)/float(address_count) * 100 )

def calculate_fccnew_techquestionable(data, geometry = None):
    fccnew_summary_categories = data['fccnew_summary_categories'] # this comes from 'categories' originally
    categories_list_one = ['copper', 'gso satellite', 'ngso satellite']
    categories_list_two = ['cable, fiber, licensed_fixed_wireless']
    if not any(category in fccnew_summary_categories for category in categories_list_two):
      if any(category in fccnew_summary_categories for category in categories_list_one):
          return 1 # tech is questionable
      else: 
          return 0 # tech is not questionable
    return 0 # default return 0????

def calculate_fccnew_need_more_ook(data, geometry = None):
    # HERE DATA is SUMMARY
    ookola_mobile_total_tests = data['ookola_mobile_total_tests']
    fccnew_max_advertised_download_speed = data['fccnew_max_advertised_download_speed']
    # Is null converted to 0?  SQL uses null comparison for fccnew_max_advertised_download_speed
    need_ook_speedtest = ookola_mobile_total_tests < 2 or fccnew_max_advertised_download_speed == 0
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

def calculate_fccnew_need_survey(data, geometry = None):
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

def calculate_fccnew_speed_questionable(data, geometry = None):
    fccnew_summary_speedtier = data['fccnew_summary_speedtier']
    no_service = ('No Service' in fccnew_summary_speedtier)
    fccnew_max_advertised_download_speed = data['fccnew_max_advertised_download_speed']
    fccnew_max_advertised_upload_speed = data['fccnew_max_advertised_upload_speed']
    speed_questionable = int((fccnew_max_advertised_download_speed <= 25 and fccnew_max_advertised_upload_speed <= 3 ) or no_service)

    return speed_questionable

def calculate_fccold_techquestionable(data, geometry = None):
    fccold_summary_category = data['fccold_summary_category']
    categories_list_one = ['DSL', 'Satellite']
    categories_list_two = ['Cable', 'Fiber', 'Fixed Wireless']

    if not any(category in fccold_summary_category for category in categories_list_one):
      if any(category in fccold_summary_category for category in categories_list_two):
          return 1 # tech is questionable
      else: 
          return 0 # tech is not questionable
    return 0 # default return 0????


def calculate_fccold_need_more_ook(data, geometry = None):
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

def calculate_fccold_need_survey(data, geometry = None):
    # DATA
    tech_questionable = data['fccold_techquestionable']
    ookola_mobile_total_tests = data['ookola_mobile_total_tests']
    fccold_all_max_down = data['fccold_all_max_down']
    ookola_mobile_avg_d_mbps = data['ookola_mobile_avg_d_mbps']
    address_count = data['address_count']
    state_survey_count = data['state_survey_count']
    state_survey_maxdownload = data['state_survey_maxdownload']

    # CALCULATIONS
    need_ncsur = 0
    if (address_count/state_survey_count) < .1 or not state_survey_count:
        need_ncsur = 1
    ook_speedtestsless = int(ookola_mobile_total_tests > 1 and ookola_mobile_avg_d_mbps < fccold_all_max_down)
    ncsur_peedtestsless = int(address_count/state_survey_count > .1 and state_survey_maxdownload < fccold_all_max_down)
    return_value = 0
    if need_ncsur:
        return_value = tech_questionable + ook_speedtestsless + ncsur_peedtestsless
    return return_value

def calculate_fccold_speed_questionable(data, geometry = None):
    fccold_summary_speedtier = data['fccold_summary_speedtier']
    no_service = ('No Service' in fccold_summary_speedtier)
    fccold_all_max_down = data['fccold_all_max_down']
    fccold_all_max_up = data['fccold_all_max_up']
    speed_questionable = int((fccold_all_max_down <= 25 and fccold_all_max_up <= 3 ) or no_service)
    return speed_questionable

def calculate_fccnew_questionable(data, geometry = None):
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
        fccnew_max_advertised_download_speed = data['fccnew_max_advertised_download_speed']

        speed_questionable = data['fccnew_speed_questionable']
        ncsur_speed_questionable = int(state_survey_maxdownload <= 25 and state_survey_maxupload <= 3)
        ookola_speed_questionable = int(ookola_mobile_avg_d_mbps <= 25 and ookola_mobile_avg_u_mbps <= 3)
        ook_speedtestsless = int(ookola_mobile_total_tests > 1 and ookola_mobile_avg_d_mbps < fccnew_max_advertised_download_speed)
        ncsur_peedtestsless = int(address_count/state_survey_count > .1 and state_survey_maxdownload < fccnew_max_advertised_download_speed)

        return speed_questionable + ncsur_speed_questionable + ookola_speed_questionable + tech_questionable + ook_speedtestsless + ncsur_peedtestsless

    return 0

def calculate_fccold_questionable(data, geometry = None):
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

def get_func(field_name):
    summ_funcs = {'fccnew_summary_speedtier': calculate_fccnew_summary_speedtier,
        'fccnew_speedtier': calculate_fccnew_speedtier,
        'address_persqmeter': calculate_address_persqmeter,
        'percent_addresses': calculate_percent_addresses,
        'fccnew_techquestionable': calculate_fccnew_techquestionable,
        'fccnew_need_more_ook': calculate_fccnew_need_more_ook,
        'fccnew_need_survey': calculate_fccnew_need_survey,
        'fccnew_speed_questionable': calculate_fccnew_speed_questionable,
        'fccold_techquestionable': calculate_fccold_techquestionable,
        'fccold_need_more_ook': calculate_fccold_need_more_ook,
        'fccold_need_survey': calculate_fccold_need_survey,
        'fccold_speed_questionable': calculate_fccold_speed_questionable,
        'fccnew_questionable': calculate_fccnew_questionable,
        'fccold_questionable': calculate_fccold_questionable
        }
    return summ_funcs[field_name]

