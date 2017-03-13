from central.config import UrlConfig

config = UrlConfig('http://date.jsontest.com/')
config.load()

print(config.get_str('time'))
print(config.get_int('milliseconds_since_epoch'))
print(config.get_str('date'))
