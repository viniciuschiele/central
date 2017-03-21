import boto3

from central.config.dynamodb import DynamoDBConfig

dynamodb = boto3.resource('dynamodb')

config = DynamoDBConfig(dynamodb, 'configurations')
config.load()

print(config.get('database.host'))
print(config.get('database.port'))
