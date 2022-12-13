try:
  import unzip_requirements
except ImportError:
  pass
from arcgis import GIS
import json, os, geopandas, pandas, requests, boto3

# portal_url = "https://thisWillFail.maps.arcgis.com"
# portal_user = "notAUser"
# portal_password = "alsoNotAPassword"

#gis = GIS(url=portal_url, username=portal_user, password=portal_password)
gis = GIS()
s3_client = boto3.client("s3")
S3_BUCKET_NAME = 'broadband-agol-data'

def broadband(event, context):
    body = {
        "message": "Go Serverless v2.0! Your function executed successfully!",
        "input": event,
    }

    try:
        print("ArcGIS Online as anonymous user")
        print("Logged in as anonymous user to " + gis.properties.portalName)

        test_input_file = 'sample input:output data/wnc_broadband_areas-THIS-IS-THE-USER-GENERATED-DATA-OR-THE-INPUT.gpkg'
        s3_file_content = s3_client.get_object(Bucket=S3_BUCKET, Key=test_input_file).read()
        test_input_file_read = geopandas.read_file(s3_file_content)
        print(test_input_file_read)
    except Exception as e:
        print(e)

    return {"statusCode": 200, "body": json.dumps(body)}
