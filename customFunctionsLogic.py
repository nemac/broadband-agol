"""This file will only exist until we migrate it to the actual real custom function file
We can delete this when done.
Every function in here is a special use case for the fields that require calculations
from previous calculations
"""

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
    return 'dummy_value_fccnew_speedtier'

def calculate_address_persqmeter(data):
    return 0

def calculate_percent_addresses(data):
    return 987654321

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