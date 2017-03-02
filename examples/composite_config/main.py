from configd.config import CompositeConfig, FileConfig

config = CompositeConfig()
config.add_config('ini', FileConfig('config.ini'))
config.add_config('json', FileConfig('config.json'))
config.load()

print(config.get('global.timeout', cast=int))  # returns an int
print(config.get('database', cast=dict))  # returns a dict
print(config.get('database.host', cast=str))  # returns a srt
print(config.get('database.port', cast=int))  # returns an int
