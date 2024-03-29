from arcgis import GIS
from arcgis.features import Feature
from copy import deepcopy
import json, os

# This is a helper utility script to do common things with the AGOL Python API

agol_username = os.environ['AGOL_USERNAME']
agol_password = os.environ['AGOL_PASSWORD']
gis = GIS("https://unca.maps.arcgis.com/home/index.html", agol_username, agol_password)

# test_output = "e757a5a007b64ba9b73ccb44362c2b15"
# test_content = gis.content.get(test_output)
# test_content_layer = test_content.layers[0]
# test_content_fset = test_content_layer.query()
# test_content_features = test_content_fset.features

# output_to_recover = "9cfbc22bfadb4be7b5127f50714c16a8"
# output_content = gis.content.get(output_to_recover)
# output_content_layer = output_content.layers[0]
# output_content_fset = output_content_layer.query()
# output_content_features = output_content_fset.features

def change_field_properties(agol_id, field):
    """The purpose of this function is to take a field definition and update the layer with that definition
    e.g. if you wanted to change the "isparkway" field type from Integer to String - this would do that
    It's pretty hardcoded - but I am writing this just so I don't keep forgetting how to do this"""
    if not field:
        print('need field yo')
        return
    content = gis.content.get(agol_id)
    content_layer = content.layers[0]
    # print out the definition before the update
    for content_field in content_layer.properties.fields:
        if field['name'] == content_field['name']:
            print('before update')
            print(content_field)
    # update the definition
    content_layer.manager.update_definition({"fields": [field]})

    # print out the definition after the update. Have to get the layer again.
    content = gis.content.get(agol_id)
    content_layer = content.layers[0]
    for content_field in content_layer.properties.fields:
        if field['name'] == content_field['name']:
            print('after update')
            print(content_field)


field = {
  "name": "fccnew_questionable",
  "type": "esriFieldTypeString",
  #"type": "esriFieldTypeInteger",
  "alias": "fccnew_questionable",
  "length": 255,
  "sqlType": "sqlTypeOther",
  "nullable": True,
  "editable": True,
  "domain": None,
  "defaultValue": None
}

def delete_feature(agol_id, feature_name):
    """The purpose of this function is to delete a specific Feature Layer Collection feature by name"""
    content = gis.content.get(agol_id)
    content_layer = content.layers[0]
    content_layer_feature_set = content_layer.query()
    content_features = content_layer_feature_set.features
    # select feature from feature_name
    selected_feature = [f for f in content_features if f.attributes['project_name'] == feature_name][0]
    # Note that examples use objectid but it appears that we are using fid and will need to delete by fid
    id_to_delete = selected_feature.get_value('fid')
    delete_result = content_layer.edit_features(deletes=[str(id_to_delete)])
    print(delete_result)


#change_field_properties("e757a5a007b64ba9b73ccb44362c2b15", field) # test data set
#change_field_properties("9cfbc22bfadb4be7b5127f50714c16a8", field) # real data set
delete_feature("9cfbc22bfadb4be7b5127f50714c16a8", "will-this-update-jeff-feb-6") # real data set

#feature_to_add = test_content_features[4] # Franklin Area

#print(feature_to_add)

#update_result = output_content_layer.edit_features(adds=[feature_to_add])
#print(update_result)

#print(test_content_features[-1])
#id_field = dict(deepcopy(test_content.layers[0].properties.fields[1]))

#print(output_content.layers[0].manager)