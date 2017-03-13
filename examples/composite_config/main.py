from central.config import CompositeConfig, FileConfig

config = CompositeConfig()
config.add_config('ini', FileConfig('config.ini'))
config.add_config('json', FileConfig('config.json'))
config.load()

print(config.get_int('global.timeout'))
print(config.get_dict('database'))
print(config.get_str('database.host'))
print(config.get_int('database.port'))
