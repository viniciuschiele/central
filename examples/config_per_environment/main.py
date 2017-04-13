from central.config import MergeConfig
from central.config.file import FileConfig


config = MergeConfig(
    FileConfig('config.json'),
    FileConfig('config.local.json')
)

config.load()

print(config.get('timeout'))
print(config.get('database'))

# you can set APP_ENV by using environment variables

# export APP_ENV=prod
# python main.py
