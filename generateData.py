import geopandas
import os
import json
import boto3
import numpy as np

import summaryFunctions
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
        gpkg_data = {gpkg_file: geopandas.read_file(s3_client.get_object(
            Bucket=S3_BUCKET, Key=gpkg_file)['Body']) for gpkg_file in all_s3_gpkg_keys}

    print('done!')
    return gpkg_data


def copy_input(id, field_name, src_data):
    # return 1st (only) geoseries element (all fields) matched by id
    target_field = fields_config[field_name]['sourcefields'][0]
    value = src_data.loc[src_data['objectid'] == id][target_field].iloc[0]
    if field_name == 'geometry':
        print('looks like geometry is coming back as an object so returning something else')
        print('that way we can override it easily in handler.py')
        return_value = "this will be easily overwritten"
        return return_value
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
    EMPTYLISTFIX = '[]'
    print(f'getting data for {field_name}')
    task = fields_config[field_name]['operation']
    if len(fields_config[field_name]['sourcefields']) == 0:
        print('no sourcefield given, returns empty...')
        return EMPTYFIX
    ret_values = src_data[src_data['geometry'].map(
        lambda shape: shape.intersects(poly))]  # geoseries of intersections
    if len(ret_values) and field_name.startswith('census'):
        print(f'census is getting in here {field_name}')
        ret_values = ret_values.loc[ret_values['year'] == 2019]
    if len(ret_values):
        all_values = np.nan_to_num(
            np.array(list(ret_values[fields_config[field_name]['sourcefields'][0]])), NANFIX)  # single values for sourcefield
    else:
        all_values = np.array([])
    print(f'values: {all_values}')

    if task == 'AVERAGE':  # Take an average across all intersections
        if not len(all_values):  # Geometry does not intersect data region
            return EMPTYFIX
        # Convert None to 0 and also convert all strings to int/double/float
        all_values = ([eval(str(0) if value is None else str(value)) for value in all_values])
        return np.average(all_values)

    elif task == 'ROUNDAVERAGE':  # Take an average across all intersections
        if not len(all_values):  # Geometry does not intersect data region
            return EMPTYFIX
        # Convert None to 0 and also convert all strings to int/double/float
        all_values = ([eval(str(0) if value is None else str(value)) for value in all_values])
        return round(np.average(all_values))

    elif task == 'SUM':  # Add the values of all intersections
        if not len(all_values):  # Geometry does not intersect data region
            return EMPTYFIX
        # Convert None to 0 and also convert all strings to int/double/float
        all_values = ([eval(str(0) if value is None else str(value)) for value in all_values])
        return np.sum(all_values)

    elif task == 'COUNT':  # Count the intersections by id
        return len(all_values)
    
    elif task == 'COUNTUNIQUE':
        return len(set(list(all_values)))

    elif task == 'MAX':
        if not len(all_values):  # Geometry does not intersect data region
            return EMPTYFIX
        # Convert None to 0 and also convert all strings to int/double/float
        all_values = ([eval(str(0) if value is None else str(value)) for value in all_values])
        return np.max(all_values)

    elif task == 'MIN':
        if not len(all_values):  # Geometry does not intersect data region
            return EMPTYFIX
        # Convert None to 0 and also convert all strings to int/double/float
        all_values = ([eval(str(0) if value is None else str(value)) for value in all_values])
        return np.min(all_values)

    elif task == 'LIST':
        if not len(all_values):
            return EMPTYLISTFIX

    elif task == 'NONZERO':
        return bool(len(all_values))

    elif task == 'SET':
        return str(set(list(all_values)))

    elif task == 'COUNTEQVALUE':
        return np.count_nonzero(all_values == fields_config[field_name]['eqValue'])

    else:
        raise Exception('Could not complete, unknown Operation:', task)


def generate_data(input_geojson, debug=False):
    """This function takes an input from user and generates all data
    for all fields (contained in output_file), then returns a dataframe
    of the new data.  The newly returned data should contain all data
    from the output file appended with new features being generated 
    and processed from the input data.


    :return: A dict containing ALL data to be sent back to AGOL and replace previous data.
    :rtype: dict """

    # CHECK FOR NEW ENTRIES
    print(input_geojson)
    deserialized_input = json.loads(input_geojson)
    input_data = geopandas.read_file(input_geojson)
    input_data = input_data.to_crs('3857')
    geometry = input_data['geometry']
    id = deserialized_input['properties']['objectid']
    gpkg_data = {}

    # Generate output dictionary, blank for now
    summary_dict = {f: None for f in fields_config}

    # THIS BLOCK FOR DEV ONLY
    # THIS WILL MOVE TO if has_new_values
    gpkg_data = read_all_gpkgs(debug=debug)

    first_round_ops = []
    second_round_ops = []
    third_round_ops = []
    fourth_round_ops = []

    for fname in fields_config:
        if fields_config[fname]['order'] == 1:
            first_round_ops.append(fname)
        elif fields_config[fname]['order'] == 2:
            second_round_ops.append(fname)
        elif fields_config[fname]['order'] == 3:
            third_round_ops.append(fname)
        elif fields_config[fname]['order'] == 4:
            fourth_round_ops.append(fname)
    # for id in test_ids:
    # FIRST GET QUERIED INPUT GEOMETRY TO INTERSECT
    # return 1st (only) geoseries geometry element matched by id
    poly_of_interest = input_data.loc[input_data['objectid']
                                      == id]['geometry'].iloc[0]

    for field in first_round_ops:
        try:
            gpkg_src_file = fields_config[field]['sourcefile']
        except:
            print('cannot find entry for field:')
            print(field)
        src_data = gpkg_data[gpkg_src_file]
        summary_dict[field] = get_field_data(
            field, poly_of_interest, src_data)

    for field in second_round_ops:
        print(f'second round ops field: {field}')
        function_to_use = summaryFunctions.get_func(field)
        summary_dict[field] = function_to_use(summary_dict, geometry)
    for field in third_round_ops:
        print(f'third round ops field: {field}')
        function_to_use = summaryFunctions.get_func(field)
        summary_dict[field] = function_to_use(summary_dict, geometry)
    for field in fourth_round_ops:
        print(f'fourth round ops field: {field}')
        function_to_use = summaryFunctions.get_func(field)
        summary_dict[field] = function_to_use(summary_dict, geometry)

    # Pop these for now since they are incompatible with the final update
    # summary_dict.pop('id')
    # summary_dict.pop('creationdate')
    # summary_dict.pop('creator')
    # summary_dict.pop('editdate')
    # summary_dict.pop('editor')
    # summary_dict.pop('globalid')
    # summary_dict.pop('fccnew_questionable') # FUNC2
    # summary_dict.pop('fccold_questionable') # FUNC2
    # summary_dict.pop('rdof_auctions_count') # FUNC1
    # summary_dict.pop('fccnew_techquestionable') # FUNC1
    # summary_dict.pop('fccnew_summary_speedtier') # FUNC1
    # summary_dict.pop('address_persqmeter') # FUNC1
    # summary_dict.pop('percent_addresses') # FUNC1
    # summary_dict.pop('adress_rank') # FUNC1
    # summary_dict.pop('fccnew_speed_questionable') # FUNC1
    # summary_dict.pop('fccnew_need_more_ook') # FUNC1
    # summary_dict.pop('fccnew_need_survey') # FUNC1
    # summary_dict.pop('fccold_techquestionable') # FUNC1
    # summary_dict.pop('fccold_need_more_ook') # FUNC1
    # summary_dict.pop('fccold_need_survey') # FUNC1
    # summary_dict.pop('fccold_speed_questionable') # FUNC1
    # summary_dict.pop('fccold_all_count_of_providers') #COUNTUNIQUE
    # summary_dict.pop('fccnew_summary_speedrank') #ROUNDAVERAGE
    # summary_dict.pop('fccnew_speedrank') #ROUNDAVERAGE

    return {'attributes': summary_dict}

if __name__ == '__main__':
    input_geojson = """{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[-82.53022941320671,35.5384577834048],[-82.53027232855094,35.533359109750386],[-82.51812728613118,35.53314956828416],[-82.51907142370445,35.538527625999315],[-82.53022941320671,35.5384577834048]]]},
    "properties":{"project_name":"test-with-new-functions","_date":1674838800000,"globalid":"{A09FB839-4BFC-4190-880F-206802B7AAC9}","objectid":20}}"""
    pprint(generate_data(input_geojson))

