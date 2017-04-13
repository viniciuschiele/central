from central.config import ModuleConfig

config = ModuleConfig('config')
config.load()

print(config.get('timeout'))
print(config.get('database'))
print(config.get('database.host'))
print(config.get('database.port'))
