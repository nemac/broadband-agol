import geopandas, os, json, glob
import numpy as np

#WE WILL PROBABLY RENAME THESE GLOBALS

#sample_dir points to the dir containing our src gpkgs with all the data
sample_dir = os.path.join(os.getcwd(), 'gpkgs')
#input_path points to latest user input file
input_path = os.path.join(sample_dir, 'outputs/wnc_broadband_areas-THIS-IS-THE-USER-GENERATED-DATA-OR-THE-INPUT.gpkg')
#output_path points to our latest updated copy in s3
output_path = os.path.join(sample_dir, 'outputs/wnc_user_defined_summary-THIS-IS-THE-ONE-YOU-NEED-TO-GENERATE.gpkg')

# START BY READIN IN/OUT FILES, ALWAYS NEEDS TO HAPPEN
input_data = geopandas.read_file(input_path)
output_data = geopandas.read_file(output_path)
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
        print('debug mode, only reading ookola_fixed.gpkg')
        ookola_fixed_path = os.path.join(sample_dir, 'ookola_fixed.gpkg')
        gpkg_data = {'ookola_fixed.gpkg': geopandas.read_file(ookola_fixed_path)}
    else:
        all_gpkgs = glob.glob(os.path.join(sample_dir, '*.gpkg'))
        gpkg_data = {os.path.basename(path):geopandas.read_file(path) for path in all_gpkgs}
    print('done!')
    return gpkg_data

def get_field_data(field_name, id, src_data):
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

    task = fields_config[field_name]['operation']

    # ONLY NEED TO READ INPUT
    if task == 'COPYINPUT':
        value = src_data.loc[src_data['id'] == id][field_name].iloc[0] #return 1st (only) geoseries element

        return value
    else: # NEED TO CHECK AGAINST A SEPARATE GPKG
        # GET QUERIED GEOMETRY
        poly_of_interest = input_data.loc[input_data['id']==id]['geometry'].iloc[0] #return 1st (only) geoseries element

        if task == 'AVERAGE':
            # print(f'calculating average for {field_name}...')
            # print(src_data[src_data['geometry'].map(lambda shape: shape.intersects(poly_of_interest))])
            ret_values = src_data[src_data['geometry'].map(lambda shape: shape.intersects(poly_of_interest))]
            all_values = np.array(list(ret_values[fields_config[field_name]['sourcefields'][0]]))
            value = np.average(all_values)
            return value # Currently can return NaN
        elif task == 'SUM':
            pass
        else:
            raise Exception('Could not complete, unknown Operation:', task)

def generate_data():
    """This function takes an input from user and generates all data
    for all fields (contained in output_file), then returns a dataframe
    of the new data.  The newly returned data should contain all data
    from the output file appended with new features being generated 
    and processed from the input data.


    :return: A dataframe containing ALL data to be sent back to AGOL and replace previous data.
    :rtype: geopandas.geodataframe.GeoDataFrame """

    # CHECK FOR NEW ENTRIES
    new_ids = list(set(input_data['id']).symmetric_difference(set(output_data['id'])))
    has_new_values = len(new_ids)
    gpkg_data = {}

    if has_new_values:
        print('New values to add, reading all gpkgs...')
        # gpkg_data = read_all_gpkgs()
    else:
        print('No new values detected, no work to be done!')
        # exit() # Nothing to be done, just exit
    
    # THIS BLOCK FOR DEV ONLY
    gpkg_data = read_all_gpkgs(debug=True) # THIS WILL MOVE TO if has_new_values
    test_ids = [1, 2, 3, 4, 5]
    test_fields = ["ookola_fixed_d_mbps_21_07", "project_name", "id", "geometry"]
    output_df = output_data.copy(deep=True)
    test_output = {}
    
    # for id in new_ids:
    for id in test_ids:
        test_output[id] = {}
        # for field in fields_config.keys():
        for field in test_fields:
            gpkg_src_file = fields_config[field]['sourcefile']
            if gpkg_src_file=='USERINPUT':
                src_data = input_data
            else:
                src_data = gpkg_data[gpkg_src_file]
            test_output[id][field] = get_field_data(field, id, src_data)
    print('output data as dictionary, needs to be DF when all fields exist:')
    print(test_output)
    exit()

    ookla_data = geopandas.read_file(os.path.join(sample_dir, 'ookola_fixed.gpkg'))

    # Currently only creates fields for ookla fixed dataset
    poly_of_interest = input_data.geometry[0]
    targ_rows = ookla_data[ookla_data['geometry'].map(lambda shape: shape.intersects(poly_of_interest))] # YAY, This gets ALL The Data for a queried intersection!
    new_cols = list(set(targ_rows.columns.tolist()) - set(input_data.columns.tolist())) # These are the columns that are in the output but not the input
    form_cols = ['ookla_fixed_'+new_col for new_col in new_cols]

    # print(form_cols)
    output_df = input_data.reindex(columns = input_data.columns.tolist() + new_cols)
    for index, geom in enumerate(input_data.geometry): # Iterates all sample shapes
        raw_data = ookla_data[ookla_data['geometry'].map(lambda shape: shape.intersects(geom))]
    for i, col_name in enumerate(new_cols):
        output_df.loc[index, form_cols[i]] = raw_data[col_name].mean()
    # print(output_df)  # WE ALSO WANT TO WRITE THIS JAZZ TO S3 as a TIMESTAMP OF GOOD TIMES!!!!!!
    return output_df

if __name__ == '__main__':
    # get_field_data('id')
    generate_data()
