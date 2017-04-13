from central.config.url import UrlConfig

config = UrlConfig('http://date.jsontest.com/')
config.load()

print(config.get('time'))
print(config.get('milliseconds_since_epoch'))
print(config.get('date'))
