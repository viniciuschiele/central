from central.config import FileConfig

config = FileConfig('config.toml')
config.load()

print(config.get('global.timeout'))  # returns an int
print(config.get('database'))  # returns a dict
print(config.get('database.host'))  # returns a srt
print(config.get('database.port'))  # returns an int
