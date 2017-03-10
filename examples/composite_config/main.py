from central.config import CompositeConfig, FileConfig
from central.property import PropertyManager

config = CompositeConfig()
config.add_config('ini', FileConfig('config.ini'))
config.add_config('json', FileConfig('config.json'))
config.load()

properties = PropertyManager(config)
prop = properties.get_property('asdas').as_int(1)

print(config.get('global.timeout', cast=int))  # returns an int
print(config.get('database', cast=dict))  # returns a dict
print(config.get('database.host', cast=str))  # returns a srt
print(config.get('database.port', cast=int))  # returns an int
