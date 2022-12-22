import os
import zipfile
import geojson
import datetime as dt
from copy import deepcopy
from arcgis.gis import GIS

# authenticate
agol_username = os.environ['AGOL_USERNAME']
agol_password = os.environ['AGOL_PASSWORD']
gis = GIS("https://unca.maps.arcgis.com/home/index.html", agol_username, agol_password)

# grab geojson that we're using to update
with open ('wnc_user_defined_summary-v2.geojson') as f:
    gj = geojson.load(f)
geojson_features = gj['features']

# look for feature layer that we're going to update
# better way to do this so we definitively grab correct feature layer collection
#agol_feature_layer_collection = gis.content.search('title:wnc_user_defined_summary owner:dmichels_nemac',
#                                              item_type='Feature Layer')[1] # grab the second one since first one is v1
agol_feature_layer_collection = gis.content.search('id: 9cfbc22bfadb4be7b5127f50714c16a8 owner:dmichels_nemac',
                                              item_type='Feature Layer')[0] # wnc_user_defined_summary-v1
#agol_feature_layer_collection = gis.content.search('id: e55c7bb634e047ea8cd729dab7e98268 owner:jbliss-nemac',
#                                              item_type='Feature Layer')[0]
#agol_feature_layer_collection = gis.content.search('id: cd15d90657554bbcb2d9e20bd5b49dbd',
#                                              item_type='Feature Layer')[0] # layer connected to the current api call
agol_feature_layer = agol_feature_layer_collection.layers[0] # grab first layer and assume it's the only one
#test_test = 'Jeff Test'
#query_string = f"project_name='{test_test}'"
#feature_set = agol_feature_layer.query(where=query_string)
feature_set = agol_feature_layer.query()
agol_feature_layer_features = feature_set.features
# def new_esri_data_dict(name):
#     esri_data_dict = {
#         "name": name,
#         "type": "esriFieldTypeDouble",
#         "alias": name,
#         #"length": 2147483647,
#         "sqlType": "sqlTypeOther",
#         "nullable": True,
#         "editable": True,
#         "domain": None,
#         "defaultValue": None
#     }
#     return esri_data_dict

#agol_feature_layer.manager.add_to_definition({"fields": [test_append]})

input_edit = agol_feature_layer_features[0]
#input_edit.attributes['new'] = 'seanIsCool'
#input_edit.attributes['creator'] = 'jeffrey'

# 1. Loop through every feature you want to update from AGOL
# 2. Loop through every geojson feature and check for matching ids
# 3. Find matching id and update with attributes that exist in both
# 4. Send updated feature back to AGOL

for feature in agol_feature_layer_features:
    feature_attribute_dict = dict(feature.attributes)
    input_edit = feature
    for gj_feature in geojson_features:
        gj_feature_properties_dict = dict(gj_feature.properties)
        if True:
        #if feature.attributes['id'] == gj_feature.properties['id']:
            #esri_data_dict = new_esri_data_dict('is_ineligible_tract')
            #agol_feature_layer.manager.update_definition({"fields": [esri_data_dict]})
            # new_keys = gj_feature_properties_dict.keys() - feature_attribute_dict.keys()
            # for key in new_keys:
            #    if(key.startswith("census_")):
            #        esri_data_dict = new_esri_data_dict(key)
            #        agol_feature_layer.manager.add_to_definition({"fields": [esri_data_dict]})
            # 
            for attribute in feature.attributes:
                 if attribute in gj_feature.properties:
                     input_edit.attributes[attribute] = gj_feature.properties[attribute]
    # send update to feature layer
    update_result = agol_feature_layer.edit_features(updates=[input_edit])
    print(update_result)
