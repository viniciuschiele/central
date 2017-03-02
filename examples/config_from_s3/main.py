#
# UPLOAD config.json into your S3 Account
#

import boto3

from configd.config.s3 import S3Config


s3 = boto3.resource('s3')

config = S3Config(s3, 'bucket-name', 'config.json')
config.load()

print(config.get('timeout'))  # returns an int
print(config.get('database'))  # returns a dict
print(config.get('database.host'))  # returns a srt
print(config.get('database.port'))  # returns an int
