from central.config import FileConfig

config = FileConfig('config.json')
config.load()

print(config.get('timeout'))
print(config.get('database'))

# you can set APP_ENV by using environment variables
# export APP_ENV=prod
# python main.py
