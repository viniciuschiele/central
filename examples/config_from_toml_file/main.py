from central.config import FileConfig

config = FileConfig('config.toml')
config.load()

print(config.get_int('global.timeout'))
print(config.get_dict('database'))
print(config.get_str('database.host'))
print(config.get_int('database.port'))
