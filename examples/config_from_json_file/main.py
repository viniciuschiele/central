from central.config import FileConfig

config = FileConfig('config.json')
config.load()

print(config.get_int('timeout'))
print(config.get_dict('database'))
print(config.get_str('database.host'))
print(config.get_int('database.port'))
