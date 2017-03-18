import requests

from central.config import FileConfig
from central.property import PropertyManager
from celery import Celery

config = FileConfig('config.json').reload_every(1000)
config.load()

properties = PropertyManager(config)
timeout = properties.get_property('timeout').as_int(10)

app = Celery()
app.config_from_object(config)


@app.task
def sync_time():
    response = requests.get('http://date.jsontest.com', timeout=timeout.get())
    data = response.json()
    time_str = data.get('time')
    # store time ...


if __name__ == '__main__':
    app.start(argv=['celery', 'worker'])
