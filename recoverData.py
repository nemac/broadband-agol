from arcgis import GIS
from arcgis.features import Feature
from copy import deepcopy
import os

agol_username = os.environ['AGOL_USERNAME']
agol_password = os.environ['AGOL_PASSWORD']
gis = GIS("https://unca.maps.arcgis.com/home/index.html", agol_username, agol_password)

test_output = "e757a5a007b64ba9b73ccb44362c2b15"
output_to_recover = "9cfbc22bfadb4be7b5127f50714c16a8"
output_content = gis.content.get(output_to_recover)
test_content = gis.content.get(test_output)
test_content_layer = test_content.layers[0]
test_content_fset = test_content_layer.query()
test_content_features = test_content_fset.features

output_content_layer = output_content.layers[0]
output_content_fset = output_content_layer.query()
output_content_features = output_content_fset.features

#feature_to_add = test_content_features[4] # Franklin Area

#print(feature_to_add)

#update_result = output_content_layer.edit_features(adds=[feature_to_add])
#print(update_result)

#print(test_content_features[-1])
#id_field = dict(deepcopy(test_content.layers[0].properties.fields[1]))

#print(output_content.layers[0].manager)