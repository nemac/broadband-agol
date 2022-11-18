try:
  import unzip_requirements
except ImportError:
  pass
from arcgis import GIS
import json, os, pandas, requests

# portal_url = "https://thisWillFail.maps.arcgis.com"
# portal_user = "notAUser"
# portal_password = "alsoNotAPassword"

#gis = GIS(url=portal_url, username=portal_user, password=portal_password)
gis = GIS()

def broadband(event, context):
    body = {
        "message": "Go Serverless v2.0! Your function executed successfully!",
        "input": event,
    }

    try:
        print("ArcGIS Online as anonymous user")
        print("Logged in as anonymous user to " + gis.properties.portalName)
    except Exception as e:
        print(e)

    return {"statusCode": 200, "body": json.dumps(body)}
