import geopandas, os

sample_dir = os.path.join(os.getcwd(), 'gpkgs')
input_file = os.path.join(sample_dir, 'outputs/wnc_broadband_areas-THIS-IS-THE-USER-GENERATED-DATA-OR-THE-INPUT.gpkg')
output_file = os.path.join(sample_dir, 'outputs/wnc_user_defined_summary-THIS-IS-THE-ONE-YOU-NEED-TO-GENERATE.gpkg')

def generate_data(input_path, output_path):
    sample_dir = os.path.join(os.getcwd(), 'gpkgs')
    input_path = os.path.join(sample_dir, 'outputs/wnc_broadband_areas-THIS-IS-THE-USER-GENERATED-DATA-OR-THE-INPUT.gpkg')
    output_path = os.path.join(sample_dir, 'outputs/wnc_user_defined_summary-THIS-IS-THE-ONE-YOU-NEED-TO-GENERATE.gpkg')

    sample_input = geopandas.read_file(input_path)
    # sample_output = geopandas.read_file(output_path)

    ookla_data = geopandas.read_file(os.path.join(sample_dir, 'ookola_fixed.gpkg'))

    # Currently only creates fields for ookla fixed dataset
    poly_of_interest = sample_input.geometry[0]
    targ_rows = ookla_data[ookla_data['geometry'].map(lambda shape: shape.intersects(poly_of_interest))] # YAY, This gets ALL The Data for a queried intersection!
    new_cols = list(set(targ_rows.columns.tolist()) - set(sample_input.columns.tolist())) # These are the columns that are in the output but not the input
    form_cols = ['ookla_fixed_'+new_col for new_col in new_cols]

    # print(form_cols)
    output_df = sample_input.reindex(columns = sample_input.columns.tolist() + new_cols)
    for index, geom in enumerate(sample_input.geometry): # Iterates all sample shapes
        raw_data = ookla_data[ookla_data['geometry'].map(lambda shape: shape.intersects(geom))]
    for i, col_name in enumerate(new_cols):
        output_df.loc[index, form_cols[i]] = raw_data[col_name].mean()
    print(output_df)
    return output_df

if __name__ == '__main__':
    generate_data(input_file, output_file)