#
# UPLOAD config.json into your S3 Account
#

import boto3

from central.config.s3 import S3Config


s3 = boto3.resource('s3')

config = S3Config(s3, 'bucket-name', 'config.json')
config.load()

print(config.get_int('timeout'))
print(config.get_dict('database'))
print(config.get_str('database.host'))
print(config.get_int('database.port'))
