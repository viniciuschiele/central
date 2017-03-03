import time
import os

from configd.config import PollingConfig, EnvironmentConfig
from configd.schedulers import FixedIntervalScheduler

os.environ['timeout'] = '10'

config = PollingConfig(EnvironmentConfig(), FixedIntervalScheduler(interval=500))
config.load()

os.environ['timeout'] = '20'

print(config.get('timeout', cast=int))

time.sleep(1)

print(config.get('timeout', cast=int))
