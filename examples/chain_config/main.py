from central.config import ChainConfig, FileConfig

config = ChainConfig([
    FileConfig('base.json'),
    FileConfig('dev.json')
])

config.load()

print(config.get('timeout'))
print(config.get('database'))
print(config.get('database.host'))
print(config.get('database.port'))
