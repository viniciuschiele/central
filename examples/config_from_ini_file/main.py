from configd.config import FileConfig

config = FileConfig('config.ini')
config.load()

print(config.get('global.timeout', cast=int))  # returns an int
print(config.get('database', cast=dict))  # returns a dict
print(config.get('database.host', cast=str))  # returns a srt
print(config.get('database.port', cast=int))  # returns an int
