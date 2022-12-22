try:
  import unzip_requirements
except ImportError:
  pass
from arcgis import GIS
from arcgis.features import Feature
from arcgis2geojson import arcgis2geojson
import json, os
from generateData import generate_data

# Define all of your constant that you will need for the function
agol_username = os.environ['AGOL_USERNAME']
agol_password = os.environ['AGOL_PASSWORD']
gis = GIS("https://unca.maps.arcgis.com/home/index.html", agol_username, agol_password)
agol_test_survey_id = "4cc4055b7cc14f08984378f2e247ea67"
agol_test_output_data_id = "d3454682e9844327be5d18fd76ef9d6b"

#agol_survey_id = "f3e35478aebf4ca08cd9ca5af3218477" # survey where polys are drawn
#agol_output_data_id = "9cfbc22bfadb4be7b5127f50714c16a8" # feature layer where data is outputted to

def broadband(event, context):
    """This function takes an incoming json payload, deserializes 
    it and parses it into geojson for processing in generateData.py. 
    Then generateData.py will return a dict and this function uses
    the arcgis connection and the dict to update the agol_output_data feature layer
    
    incoming json payload information:
    json_loads is deserialized incoming payload
    json_loads['feature']['attributes']['objectid'] = 'id' in output feature layer
    json_loads['feature']['attributes']['project_name'] = 'project_name' in output
    json_loads['feature']['geometry'] = esriGeometryPolygon that needs to be converted to geojson
    """
    body = {
        "message": "Go Serverless v2.0! Your function executed successfully!",
        "input": event['body'],
    }

    try:
        # deserialize json
        print('jeff 0')
        incoming_json = event['body']
        print('jeff 1')
        json_loads = json.loads(incoming_json)
        print('jeff 2')

        # grab all important data from the incoming payload
        incoming_feature = json_loads['feature']
        print('jeff 3')
        incoming_objectid = json_loads['feature']['attributes']['objectid']
        print('jeff 4')
        incoming_global_id = json_loads['feature']['attributes']['globalid']
        print('jeff 5')
        incoming_project_name = json_loads['feature']['attributes']['project_name']
        print('jeff 6')
        incoming_esri_geometry = json_loads['feature']['geometry']
        print('jeff 7')

        # convert feature to geojson for easier processing in generateData.py
        feature_geojson = arcgis2geojson(json.dumps(incoming_feature))
        print('jeff 8')
        print(feature_geojson)
        print('jeff 9')
        print(type(feature_geojson))
        print('jeff 10')

        # call generateData, pass it the geojson, and expect a dictionary of updates in return
        # at the moment this is commented out so we're building a dictionary ourselves below
        output_feature_layer_updates = generate_data(feature_geojson)
        print('THIS IS OUTPUT_FEATURE_LAYER_UPDATES BEFORE GEOM UPDATED')
        print(type(output_feature_layer_updates))
        print(output_feature_layer_updates)
        print('THIS IS OUTPUT_FEATURE_LAYER_UPDATES AFTER GEOM UPDATED')
        # overwrite/add geometry, fid
        output_feature_layer_updates['attributes']['geometry'] = incoming_esri_geometry
        output_feature_layer_updates['attributes']['fid'] = incoming_objectid

        print(output_feature_layer_updates)


        # Grab survey that corresponds with incoming id so we can get the rest of the attributes
        #survey = gis.content.get(agol_survey_id).layers[0]
        # print('jeff 11')
        # survey = gis.content.get(agol_test_survey_id).layers[0]
        # print('jeff 12') 
        # query_string = f"objectid='{incoming_objectid}'"
        # print('jeff 13')
        # feature_set = survey.query(where=query_string)
        # print('jeff 14')
        # survey_features_dict = feature_set.features[0].as_dict
        # print('jeff 15')
        # survey_shape_area = survey_features_dict['attributes']['Shape__Area']
        # print('jeff 16')
        # survey_shape_length = survey_features_dict['attributes']['Shape__Length']
        # print('jeff 17')
        # survey_creation_date = survey_features_dict['attributes']['CreationDate']
        # print('jeff 18')
        # survey_creator = survey_features_dict['attributes']['Creator']
        # print('jeff 19')
        # survey_edit_date = survey_features_dict['attributes']['EditDate']
        # print('jeff 20')
        # survey_editor = survey_features_dict['attributes']['Editor']
        # print('jeff 21')

        # Build a dictionary that combines the information from the incoming json and survey
        # We will send this up separately later on since we do not want to lose this information
        incoming_json_and_survey = {
            'geometry': incoming_esri_geometry,
            'attributes': {
                'id': incoming_objectid,
                'objectid': incoming_objectid,
                'globalid': incoming_global_id,
                #'Shape__Area': survey_shape_area,
                #'Shape__Length': survey_shape_length,
                #'creationdate' : survey_creation_date,
                #'creator': survey_creator,
                #'editdate': survey_edit_date,
                #'editor': survey_editor,
                'project_name': incoming_project_name 
            }
        }

        # test dictionary that is simulating return from generateData.py. Key 'objectid' MUST BE INCLUDED!!!
        # output_feature_layer_updates = {
        #     'attributes': {
        #       'objectid': incoming_objectid,
        #       'update_from_lambda' : 'hello from lambda' # the only update was 'update_from_lambda' in this case
        #     }
        # }
        
        # use AGOL API to grab output feature collection using id above
        #agol_feature_layer_collection = gis.content.get(agol_output_data_id)
        agol_feature_layer_collection = gis.content.get(agol_test_output_data_id)
        agol_feature_layer = agol_feature_layer_collection.layers[0] # grab first layer and assume it's the only one

        # use AGOL API again to find the feature layer that was just created so that we can edit it 
        #query_string = f"objectid='{incoming_objectid}'"
        # feature_set = agol_feature_layer.query(where=query_string)
        # agol_feature_layer_features = feature_set.features
        # input_edit = agol_feature_layer_features[0]
        # print(input_edit)
        # print(type(input_edit))
        #input_edit.attributes['test_field'] = 'Hello from lambda'
        #update_result = agol_feature_layer.edit_features(updates=[input_edit])

        # convert both dictionaries from above into Features to send to AGOL
        converted_feature = Feature.from_dict(incoming_json_and_survey)
        #update_result = agol_feature_layer.edit_features(updates=[converted_feature])
        #print(update_result)
        converted_feature = Feature.from_dict(output_feature_layer_updates)
        update_result = agol_feature_layer.edit_features(adds=[converted_feature])
        print(update_result)

    except Exception as e:
        print(e)

    return {"statusCode": 200, "body": json.dumps(body)}
