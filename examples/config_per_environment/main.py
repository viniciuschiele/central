from central.config import ChainConfig, FileConfig


config = ChainConfig([
    FileConfig('config.json'),
    FileConfig('config.${APP_ENV}.json')
])

config.load()

print(config.get('timeout'))
print(config.get('database'))

# you can set APP_ENV by using environment variables

# export APP_ENV=prod
# python main.py
