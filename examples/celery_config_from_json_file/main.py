from central.config import FileConfig
from celery import Celery

config = FileConfig('config.json')
config.load()

app = Celery()
app.config_from_object(config)

print(app.conf.BROKER_URL)
