from arcgis import GIS
from arcgis.features import Feature
from copy import deepcopy
import os

agol_username = os.environ['AGOL_USERNAME']
agol_password = os.environ['AGOL_PASSWORD']
gis = GIS("https://unca.maps.arcgis.com/home/index.html", agol_username, agol_password)

test_output = "d3454682e9844327be5d18fd76ef9d6b"
output_to_recover = "9cfbc22bfadb4be7b5127f50714c16a8"
output_content = gis.content.get(output_to_recover)
test_content = gis.content.get(test_output)
test_content_layer = test_content.layers[0]
test_content_fset = test_content_layer.query()
test_content_features = test_content_fset.features
print(test_content_features[-1])
#id_field = dict(deepcopy(test_content.layers[0].properties.fields[1]))

#print(output_content.layers[0].manager)