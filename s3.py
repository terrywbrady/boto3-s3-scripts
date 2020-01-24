#!/usr/bin/python
import boto3
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read('service.ini')

configkey = "minio"
configkey = "s3"

bucketName = config.get(configkey, "bucket")
#s3 = boto3.resource('s3')

s3cli = boto3.client('s3')
if (configkey == "minio"):
    s3 = boto3.cli('s3',
      aws_access_key_id=config.get(configkey, "accessKey"),
      aws_secret_access_key=config.get(configkey, "secretKey"),
      endpoint_url=config.get(configkey, "endpointUrl")
    )

list = s3cli.list_objects_v2(
    Bucket=bucketName,
    MaxKeys=5,
    Prefix=''
)

for lobj in list['Contents']:
  key=lobj['Key']
  print key
  obj = s3cli.get_object(Bucket=bucketName, Key=key)
  print obj['Metadata']

s3cli.upload_file("s3.py", bucketName, "terry/s3.py")

list = s3cli.list_objects_v2(
    Bucket=bucketName,
    MaxKeys=5,
    Prefix='terry'
)

for obj in list['Contents']:
  print obj['Key']
