import os
import zipfile
import geojson
import datetime as dt
from arcgis.gis import GIS

# authenticate
agol_username = 'ENTER_YOUR_USERNAME_HERE'
agol_password = 'ENTER_YOUR_PASSWORD_HERE'
gis = GIS("https://unca.maps.arcgis.com/home/index.html", agol_username, agol_password)

# grab geojson that we're using to update
with open ('wnc_user_defined_summary-v2.geojson') as f:
    gj = geojson.load(f)
geojson_features = gj['features']

# look for feature layer that we're going to update
# better way to do this so we definitively grab correct feature layer collection
#agol_feature_layer_collection = gis.content.search('title:wnc_user_defined_summary owner:dmichels_nemac', 
#                                              item_type='Feature Layer')[1] # grab the second one since first one is v1
agol_feature_layer_collection = gis.content.search('title:Test_Input owner:jbliss-nemac', 
                                              item_type='Feature Layer')[0] # grab the second one since first one is v1
agol_feature_layer = agol_feature_layer_collection.layers[0] # grab first layer and assume it's the only one
feature_set = agol_feature_layer.query()
agol_feature_layer_features = feature_set.features

input_edit = agol_feature_layer_features[0]
input_edit.attributes['newAttribute'] = 'seanIsCool'
input_edit.attributes['creator'] = 'jeffjeffjeff'
update_result = agol_feature_layer.edit_features(updates=[input_edit])
print(update_result)

# 1. Loop through every feature you want to update from AGOL
# 2. Loop through every geojson feature and check for matching ids
# 3. Find matching id and update with attributes that exist in both
# 4. Send updated feature back to AGOL
# for feature in agol_feature_layer_features:
#     input_edit = feature
#     for gj_feature in geojson_features:
#         if feature.attributes['id'] == gj_feature.properties['id']:
#             for attribute in feature.attributes:
#                 if attribute in gj_feature.properties:
#                     input_edit.attributes[attribute] = geojson_features[0].properties[attribute]
    # send update to feature layer
    #update_result = agol_feature_layer.edit_features(updates=[input_edit])
    #print(update_result)


#input_edit = input_feature
#input_edit.attributes['project_name'] = 'Davids Street'

#for feature in features:
    #for key, value in feature['properties'].items():
      #print(key, value)