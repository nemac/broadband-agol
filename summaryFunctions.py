import numpy as np
import json

def get_func(field_name, summary_data):
    summ_funcs = {}
    with open('fields_config.json', 'r') as jfile:
        fields_config = json.load(jfile)
    for field in fields_config:
        if fields_config[field]['order'] > 1:
            summ_funcs[field] = None
    print(summ_funcs)
    # func_dict = {"rdof_auctions_count": None,
    # "fccnew_summary_speedtier": None,
    # "fccnew_summary_speedtier": None,
    # "fccnew_speedtier": None,
    # "address_persqmeter": None,
    # "percent_addresses": None,
    #  }
