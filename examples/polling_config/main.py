from configd.config import PollingConfig, FileConfig, CompositeConfig
from configd.schedulers import FixedIntervalScheduler


config = PollingConfig(FixedIntervalScheduler(interval=1000))
config.add_config('json', FileConfig('config.json'))
config.load()

print(config.get('global.timeout', cast=int))  # returns an int
print(config.get('database', cast=dict))  # returns a dict
print(config.get('database.host', cast=str))  # returns a srt
print(config.get('database.port', cast=int))  # returns an int
