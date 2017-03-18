from central.config import FileConfig

config = FileConfig('config.json')
config.load()

print(config.get('timeout'))
print(config.get('database'))
print(config.get('database.host'))
print(config.get('database.port'))
