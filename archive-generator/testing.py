import boto3
from dateutil import parser
client = boto3.client('s3')

response = client.list_objects_v2(
    Bucket='nltl-archive',
    Prefix='')

for content in response.get('Contents', []):
    print(parser.parse(content['Key'].split(".")[0]))
