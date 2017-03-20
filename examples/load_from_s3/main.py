#
# UPLOAD config.json into your S3 Account
#

import boto3

from central.config.s3 import S3Config


s3 = boto3.resource('s3')

config = S3Config(s3, 'bucket-name', 'config.json')
config.load()

print(config.get('timeout'))
print(config.get('database'))
print(config.get('database.host'))
print(config.get('database.port'))
