import time
import os

from central.config import EnvironmentConfig

os.environ['timeout'] = '10'

config = EnvironmentConfig().reload_every(500)
config.load()

os.environ['timeout'] = '20'

print(config.get_int('timeout'))

time.sleep(1)

print(config.get_int('timeout'))
