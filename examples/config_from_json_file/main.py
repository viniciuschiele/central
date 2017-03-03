from configd.config import FileConfig

config = FileConfig('config.json')
config.load()

print(config.get('timeout'))  # returns an int
print(config.get('database'))  # returns a dict
print(config.get('database.host'))  # returns a srt
print(config.get('database.port'))  # returns an int