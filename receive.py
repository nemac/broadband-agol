"""The purpose of this function is to receive the webhook payload from 
AGOL and immediately send it on to the broadband handler and return.
This is necessary because if we do not return within 5 seconds or less
from the AGOL webook, it assumes failure and will retry. We do not want 
this retry to happen so we have to immediately return even though processing
is not complete.
"""
import boto3, json
client = boto3.client("lambda")

def handler(event, context):
    body = {
          "message": "Go Serverless v2.0! Your function executed successfully!",
          "input": event['body'],
    }

    client.invoke(
      FunctionName="broadband-agol-beta-broadband",
      InvocationType='Event',
      Payload=json.dumps(event['body'])
    )

    return {
      "statusCode": 200,
      "headers": {
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Origin': 'https://survey123.arcgis.com',
        'Access-Control-Allow-Methods': 'OPTIONS, POST, GET'
      },
      "body": "success!"
    }