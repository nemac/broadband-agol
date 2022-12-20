import geopandas
import os
import json
import glob
import boto3
import numpy as np

from pprint import pprint

# READ GPKGS FROM S3
s3_client = boto3.client("s3")
S3_BUCKET = 'broadband-agol-data'
s3_file_content = s3_client.list_objects_v2(Bucket=S3_BUCKET)['Contents']
do_not_include = [
    'sample input:output data/wnc_broadband_areas-THIS-IS-THE-USER-GENERATED-DATA-OR-THE-INPUT.gpkg',
    'sample input:output data/wnc_h3_level8_summary-YOU-DONT-NEED-TO_GENERATE-THIS.gpkg',
    'sample input:output data/wnc_user_defined_summary-THIS-IS-THE-ONE-YOU-NEED-TO-GENERATE',
    'wnc_h3_level8.gpkg']
all_s3_gpkg_keys = [obj['Key']
                    for obj in s3_file_content if not obj['Key'] in do_not_include]

output_data = geopandas.read_file(s3_client.get_object(
    Bucket=S3_BUCKET, Key='sample input:output data/wnc_user_defined_summary-THIS-IS-THE-ONE-YOU-NEED-TO-GENERATE')['Body'])
input_s3 = geopandas.read_file(s3_client.get_object(
    Bucket=S3_BUCKET, Key='sample input:output data/wnc_broadband_areas-THIS-IS-THE-USER-GENERATED-DATA-OR-THE-INPUT.gpkg')['Body'])


# Get configurations for field data
with open('fields_config.json', 'r') as jfile:
    fields_config = json.load(jfile)


def read_all_gpkgs(debug=False):
    """This function just reads all of the gpkgs contained in our
    source directory in for data processing.  This is a one-time call
    function, since we will have to inevitably read all gpkgs to
    process any new feature, and its more efficient to read them
    once, and operate from that data.

    :param debug: saves time for development by limiting to just ookola_fixed
    :type debug: bool

    :return: A dictionary in the format of {<FILENAME>:<GEOPANDAS.DATAFRAME}
    :rtype: dict """

    print('Reading all gpkgs...')

    def util_func(client, keys):
        gpkg_data = {}
        for f in keys:
            try:
                gpkg_data[f] = geopandas.read_file(s3_client.get_object(
                    Bucket=S3_BUCKET, Key=f)['Body'])
            except Exception as e:
                print(f'failed to read {f}')
                print(f'reason given: {e}')
                exit()
        return gpkg_data
    print(f"debug={debug}")
    if debug:
        file_names = ['ookola_fixed.gpkg', 'ookola_mobile.gpkg',
                      'wnc_nc_broadband_survey.gpkg', 'wnc_ineligibletracts_2022.gpkg',
                      'wnc_great_grants_round1.gpkg', 'wnc_great_grants_round2.gpkg',
                      'wnc_great_grants_round3.gpkg', 'wnc_fed_grant_areas.gpkg',
                      'wnc_address.gpkg', 'wnc_fcc_rdof_auction_904_results.gpkg',
                      'wnc_provider_boundaries_block_477.gpkg',
                      'wnc_fixed_summary_block_477.gpkg']
        print(f'debug mode, only reading {file_names}')
        file_objects = [s3_client.get_object(
            Bucket=S3_BUCKET, Key=f)['Body'] for f in file_names]
        gpkg_data = {n: geopandas.read_file(
            o) for n, o in zip(file_names, file_objects)}

    else:
        gpkg_data = util_func(s3_client, all_s3_gpkg_keys)
        # gpkg_data = {gpkg_file: geopandas.read_file(s3_client.get_object(
        #     Bucket=S3_BUCKET, Key=gpkg_file)['Body']) for gpkg_file in all_s3_gpkg_keys}

    print('done!')
    return gpkg_data


def generate_summaries(poly, data, output):

    # fccnew_working_data = {'tech_questionable': None, # CALCULATED HERE SEE FUNC
    #                        'fccnew_summary_speedtier': None, # READ IN.. STRING TO BOOL?
    #                        'speed_questionable': None, # CALCULATED HERE SEE FUNC
    #                        'ncsur_speed_questionable': None, # CALCULATED HERE state_survey_maxdownload <= 25 AND state_survey_maxupload <= 3
    #                        'state_survey_maxdownload': get_field_data('state_survey_maxdownload', poly, data[fields_config['state_survey_maxdownload']]), # READ IN MAX(dl_speed)
    #                        'state_survey_maxupload': get_field_data('state_survey_maxupload', poly, data[fields_config['state_survey_maxupload']]), #READ IN MAX(ul_speed)
    #                        'ookola_speed_questioanble': None, # CALCULATED HERE ookola_mobile_avg_d_mbps <= 25 AND ookola_mobile_avg_u_mbps <= 3
    #                        'ookola_mobile_avg_d_mbps': get_field_data('ookola_mobile_avg_d_mbps', poly, data[fields_config['ookola_mobile_avg_d_mbps']]), # READ IN OOKOLA MOBILE
    #                        'ookola_mobile_avg_u_mbps': get_field_data('ookola_mobile_avg_u_mbps', poly, data[fields_config['ookola_mobile_avg_u_mbps']]), # READ IN OOKOLA MOBILE - AVERAGE get_avg(fld, src)
    #                        'ook_speedtestsless': None, # CALCULATED HERE, mobile_total > 1 and mobile_avg_d < fccnew_max_advertised_download
    #                        'ookola_mobile_total_tests': get_field_data('ookola_mobile_total_tests', poly, data[fields_config['ookola_mobile_total_tests']]), # READ IN OOKOLA MOBILE
    #                        'ncsur_peedtestsless': None, # CALCULATED HERE, ookola_mobile_total_tests > 1 and ookola_mobile_avg_d_mbps < fccnew_max_advertised_download_speed
    #                        'fccnew_summary_categories': None, # READ IN AND CALCULATED FROM CATEGORY
    #                        'need_ook_speedtest': None, # CALCULATED HERE (ookola_mobile_total_tests > 1 and ookola_mobile_avg_d_mbps < fccnew_max_advertised_download_speed)
    #                        'need_ncsur': None, # CALCULATED HERE address_count/state_survey_count < .1 or state_survey_count is null
    #                        'address_count': get_field_data('address_count', poly, data[fields_config['address_count']]), # READ IN FROM WNC_ADDRESS
    #                        'state_survey_count': get_field_data('state_survey_count', poly, data[fields_config['state_survey_count']]), #READ IN FROM WNC_NC_SURVEY - COUNT ID's Returned from intersection
    #                        'fccnew_max_advertised_download_speed': get_field_data('fccnew_max_advertised_download_speed', poly, data[fields_config['fccnew_max_advertised_download_speed']]), # READ IN FCC NEW NEX
    #                        'fccnew_max_advertised_upload_speed': get_field_data('fccnew_max_advertised_upload_speed', poly, data[fields_config['fccnew_max_advertised_upload_speed']])} # READ IN FCC NEW HEX
    # fccold_working_data = {'tech_questionable': None, # CALCULATED HERE SEE FUNC
    #                        'fccold_summary_speedtier': get_field_data('fccold_summary_speedtier', poly, data[fields_config['fccold_summary_speedtier']]), # READ IN.. STRING TO BOOL?
    #                        'speed_questionable': None,# CALCULATED HERE SEE FUNC
    #                        'ncsur_speed_questionable': None, # CALCULATED HERE state_survey_maxdownload <= 25 AND state_survey_maxupload <= 3
    #                        'ookola_speed_questioanble': None, # CALCULATED HERE ookola_mobile_avg_d_mbps <= 25 AND ookola_mobile_avg_u_mbps <= 3
    #                        'ookola_mobile_avg_d_mbps': get_field_data('ookola_mobile_avg_d_mbps', poly, data[fields_config['ookola_mobile_avg_d_mbps']]), # READ IN OOKOLA MOBILE
    #                        'ookola_mobile_avg_u_mbps': get_field_data('ookola_mobile_avg_u_mbps', poly, data[fields_config['ookola_mobile_avg_u_mbps']]), # READ IN OOKOLA MOBILE - AVERAGE get_avg(fld, src)
    #                        'ook_speedtestsless': None, # CALCULATED HERE, ookola_mobile_total_tests > 1 and ookola_mobile_avg_d_mbps < fccnew_max_advertised_download_speed
    #                        'ookola_mobile_total_tests': None, # READ IN OOKOLA MOBILE
    #                        'ncsur_peedtestsless': None,# CALCULATED HERE, ookola_mobile_total_tests > 1 and ookola_mobile_avg_d_mbps < fccnew_max_advertised_download_speed
    #                        'fccold_summary_categories': None,
    #                        'need_ook_speedtest': None,
    #                        'need_ncsur': None,
    #                        'address_count': get_field_data('address_count', poly, data[fields_config['address_count']]), # READ IN FROM WNC_ADDRESS
    #                        'state_survey_count': get_field_data('state_survey_count', poly, data[fields_config['state_survey_count']]), #READ IN FROM WNC_NC_SURVEY - COUNT ID's Returned from intersection
    #                        'fccold_all_max_down': get_field_data('fccold_all_max_down', poly, data[fields_config['fccold_all_max_down']]), # READ IN
    #                        'fccold_all_max_up': get_field_data('fccold_all_max_up', poly, data[fields_config['fccold_all_max_up']])} # READ IN

    gen_fields = ['questionable', 'techquestionable', 'need_more_ook',
                  'need_survey', 'speed_questionable']

    fccnew_input_fields = {'new_fcc_hex3_I8.gpkg': ['max_advertised_download_speed',
                                                    'max_advertised_upload_speed', 'category', 'speedtier', 'speedrank'],
                           'ookola_mobile.gpkg': ['ookola_mobile_total_tests', 'ookola_mobile_avg_d_mbps']}
    fccold_input_fields = {'wnc_provider_boundaries_block_477.gpkg': [],
                           'wnc_fixed_summary_block_477.gpkg': []}

    fccold_summ = {
        f"fccold_{field}": fccold_working_data[field] for field in gen_fields}
    fccnew_summ = {
        f"fccnew_{field}": fccnew_working_data[field] for field in gen_fields}
    return fccold_summ, fccnew_summ

    # NEED TO DEFINE GENERATORS FOR EACH SUMMARY FIELD
    def fcc_new_questionable(poly, src):
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

    def fcc_new_techquestionable(poly, src):
        '''CONDITION:
        case when 
                  (fccnew_summary_categories like '%copper%' or fccnew_summary_categories like '%gso satellite%' or fccnew_summary_categories like '%ngso satellite%') 
                  AND
                  not(fccnew_summary_categories  like '%cable%' or fccnew_summary_categories  like '%fiber%' or fccnew_summary_categories  like '%licensed_fixed_wireless%' or fccnew_summary_categories  like '%unlicensed_fixed_wireless%') then 1 else 0 end  tech_questionable
          '''
        # ORDER: 1
        '''NEEDED FIELDS:
          fccnew_summary_categories
          '''
        print('istechquestionable')

    def fcc_new_need_more_ook(poly, src):
        '''CONDITION:
        case when need_ook_speedtest = 1 then tech_questionable + ook_speedtestsless + ncsur_peedtestsless else 0 end as need_more_ook,'''
        # ORDER: 2
        '''NEEDED FILES:
        need_ook_speedtest
        tech_quesitonable > calculated
        ook_speedtestlsless
        ncsur_peedtestsless'''
        print('need_more_ook')

    def fcc_new_need_survey(poly, src):
        '''CONDITON:
        case when need_ncsur = 1 then tech_questionable + ook_speedtestsless + ncsur_peedtestsless else 0 end as need_survey	'''
        # ORDER: 2
        '''NEEDED FIELDS:
        ncsur
        tech_questionable > calculated here
        ook_speedtestsless
        ncsur_peedtestsless'''
        print('need_survey')

    def fcc_new_speed_questionable(poly, src):
        '''CONDITON: case when (fccnew_max_advertised_download_speed <= 25 AND fccnew_max_advertised_upload_speed <= 3 ) OR  fccnew_summary_speedtier like '%No Service%' then 1 else 0 end speed_questionable,'''
        # ORDER: 1
        '''NEEDED FIELDS:
        fccnew_max_advertised_download_speed
        fccnew_max_advertised_upload_speed
        fccnew_summary_speedtier
        '''
        print('speed_questionable')

    def fcc_old_questionable(poly, src):
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

    def fcc_old_techquestioanble(poly, src):
        # NOT SURE WHERE TO FIND SUMMARY_CATEGORY...
        '''CONDITION:
        case when 
                  (fccold_summary_category like '%DSL%' or fccold_summary_category like 'Satellite%') 
                  AND
                  (fccold_summary_category not like '%Cable%' or fccold_summary_category not like '%Fiber%' or fccold_summary_category not like '%Fixed Wireless%') 
                then 1 else 0 end tech_questionable,'''
        # ORDER: 1
        '''NEEDED FIELDS:
        fccold_summary_category'''
        print('fcc_old_techquestionable')

    def fcc_old_need_more_ook(poly, src):
        '''CONDITION:
        case when need_ook_speedtest = 1 then tech_questionable + ook_speedtestsless + ncsur_peedtestsless else 0 end as need_more_ook,'''
        # ORDER: 2
        '''NEEDED FIELDS:
        need_ook_speedtest
        tech_quesitonable > calculated
        ook_speedtestlsless
        ncsur_peedtestsless'''
        print('fcc_old_need_more_ook')

    def fcc_old_need_survey(poly, src):
        '''CONDITION:
        case when need_ncsur = 1 then tech_questionable + ook_speedtestsless + ncsur_peedtestsless else 0 end as need_survey'''
        # ORDER: 2
        '''NEEDED FIELDS:
        tech_quesitonable > calculated
        ook_speedtestsless
        ncsur_peedtestsless'''
        print('fcc_old_need_survey')

    def fcc_old_speed_questionable(poly, src):
        '''CONDITION:
        case when (fccold_all_max_down <= 25 AND fccold_all_max_up <= 3 ) or fccold_summary_speedtier like '%No Service%'  then 1 else 0 end speed_questionable,'''
        # ORDER: 1
        '''NEEDED FILES:
        fccold_all_max_down
        fccold_all_max_up
        fccold_summary_speedtier'''
        print('fcc_old_speed_questionable')


def copy_input(id, field_name, src_data):
    # return 1st (only) geoseries element (all fields) matched by id
    target_field = fields_config[field_name]['sourcefields'][0]
    value = src_data.loc[src_data['objectid'] == id][target_field].iloc[0]
    return value


def get_field_data(field_name, poly, src_data):
    """This function takes in a geometry and returns the target
    field data matching all intersections (or direct copied for 
    field values from user input).

    :param field_name: Field to return data for
    :type field_name: String
    :param id: to select correct output feature
    :type id: Integer
    :param src_data: geopandas data frame to read from
    :type src_data: geopandas.geodataframe.GeoDataFrame

    :return: A single value, aggregated using the field's operation from config
    :rtype: String || double || int || bool """
    NANFIX = 0  # This WILL be read from config per field
    EMPTYFIX = 0  # This WILL be read from config per field
    EMPTYLISTFIX = []
    print(f'getting data for {field_name}')
    task = fields_config[field_name]['operation']
    if len(fields_config[field_name]['sourcefields']) == 0:
        print('no sourcefield given, returns empty...')
        return EMPTYFIX
    ret_values = src_data[src_data['geometry'].map(
        lambda shape: shape.intersects(poly))]  # geoseries of intersections
    if len(ret_values):
        all_values = np.nan_to_num(
            np.array(list(ret_values[fields_config[field_name]['sourcefields'][0]])), NANFIX)  # single values for sourcefield
    else:
        all_values = np.array([])
    if task == 'AVERAGE':  # Take an average across all intersections
        if not len(all_values):  # Geometry does not intersect data region
            return EMPTYFIX
        value = np.average(all_values)
        return value  # Currently can return NaN, need to handle that
    elif task == 'SUM':  # Add the values of all intersections
        if not len(all_values):  # Geometry does not intersect data region
            return EMPTYFIX
        return np.sum(all_values)
    elif task == 'COUNT':  # Count the intersections by id
        return len(all_values)
    elif task == 'MAX':
        if not len(all_values):  # Geometry does not intersect data region
            return EMPTYFIX
        # Currently can return NaN, need to handle that
        return np.max(all_values)
    elif task == 'MIN':
        if not len(all_values):  # Geometry does not intersect data region
            return EMPTYFIX
        # Currently can return NaN, need to handle that
        return np.min(all_values)
    elif task == 'LIST':
        if not len(all_values):
            return EMPTYLISTFIX
    elif task == 'NONZERO':
        return bool(len(all_values))
    elif task == 'SET':
        return set(list(all_values))
    else:
        raise Exception('Could not complete, unknown Operation:', task)


def generate_data(input_data=input_s3, debug=False):
    """This function takes an input from user and generates all data
    for all fields (contained in output_file), then returns a dataframe
    of the new data.  The newly returned data should contain all data
    from the output file appended with new features being generated 
    and processed from the input data.


    :return: A dict containing ALL data to be sent back to AGOL and replace previous data.
    :rtype: dict """

    # CHECK FOR NEW ENTRIES
    deserialized_input = json.load(input_data)
    id = deserialized_input['properties']['objectid']
    print(id)
    gpkg_data = {}

    # Generate output dictionary, blank for now
    output_dict = {f: fields_config[f]['operation'] for f in fields_config}

    # THIS BLOCK FOR DEV ONLY
    # THIS WILL MOVE TO if has_new_values
    gpkg_data = read_all_gpkgs(debug=debug)
    # test_ids = [1, 2, 3, 4, 5]
    test_fields = ["ookola_fixed_d_mbps_21_07",
                   "project_name", "id", "geometry"]
    first_round_ops = ['AVERAGE', 'SUM', 'COUNT', 'LIST',
                       'MAX', 'MIN', 'NONZERO', 'SET']

    # for id in test_ids:
    # FIRST GET QUERIED INPUT GEOMETRY TO INTERSECT
    # return 1st (only) geoseries geometry element matched by id
    poly_of_interest = input_data.loc[input_data['objectid']
                                      == id]['geometry'].iloc[0]
    # fccold_summ, fccnew_summ = generate_summaries(poly_of_interest, gpkg_data)

    # for field in fields_config.keys():
    for field in output_dict:
        # for field in test_fields:
        try:
            gpkg_src_file = fields_config[field]['sourcefile']
        except:
            print('cannot find entry for field:')
            print(field)
            exit()
        # HANDLE SPECIAL CASES where data is input or summary
        if fields_config[field]['operation'] == 'COPYINPUT':
            output_dict[field] = copy_input(id, field, input_data)
        else:
            if gpkg_src_file == 'TBD':
                print(f'skipping {field}')
            # if gpkg_src_file == 'FCCNEW':
            #     src_data = fccnew_summ
            # elif gpkg_src_file == 'FCCOLD':
            #     src_data = fccold_summ
            elif fields_config[field]['operation'] in first_round_ops:
                src_data = gpkg_data[gpkg_src_file]
                output_dict[field] = get_field_data(
                    field, poly_of_interest, src_data)
    final_output = {'attributes': output_dict}
    return final_output

    ookla_data = geopandas.read_file(
        os.path.join(sample_dir, 'ookola_fixed.gpkg'))

    # Currently only creates fields for ookla fixed dataset
    poly_of_interest = input_data.geometry[0]
    targ_rows = ookla_data[ookla_data['geometry'].map(lambda shape: shape.intersects(
        poly_of_interest))]  # YAY, This gets ALL The Data for a queried intersection!
    # These are the columns that are in the output but not the input
    new_cols = list(set(targ_rows.columns.tolist()) -
                    set(input_data.columns.tolist()))
    form_cols = ['ookla_fixed_'+new_col for new_col in new_cols]

    # print(form_cols)
    output_df = input_data.reindex(
        columns=input_data.columns.tolist() + new_cols)
    # Iterates all sample shapes
    for index, geom in enumerate(input_data.geometry):
        raw_data = ookla_data[ookla_data['geometry'].map(
            lambda shape: shape.intersects(geom))]
    for i, col_name in enumerate(new_cols):
        output_df.loc[index, form_cols[i]] = raw_data[col_name].mean()
    # print(output_df)  # WE ALSO WANT TO WRITE THIS JAZZ TO S3 as a TIMESTAMP OF GOOD TIMES!!!!!!
    return output_df


if __name__ == '__main__':
    input_geojson = """{"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[-83.24920801364088, 35.24898181734354], [-83.24920801364088, 35.24891172352602], [-83.2491060896983, 35.24897305561967], [
        -83.24920801364088, 35.24898181734354]]]}, "properties": {"project_name": "dsfdsafdsdsffds fssdf sdfsdf", "_date": 1671037200000, "globalid": "{31724E0B-CE20-4965-82ED-0A6AA55DABC8}", "objectid": 8}}"""
    test_input = geopandas.read_file(input_geojson)
    pprint(generate_data(test_input))
    # get_field_data('id')
    # pprint(generate_data())
