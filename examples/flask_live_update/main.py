import requests

from central.config.file import FileConfig
from central.property import PropertyManager
from flask import Flask

config = FileConfig('config.json').reload_every(1000)
config.load()

properties = PropertyManager(config)
timeout = properties.get_property('timeout').as_int(10)

app = Flask(__name__)
app.config.from_mapping(config)


@app.route('/time')
def get_current_time():
    response = requests.get('http://date.jsontest.com', timeout=timeout.get())
    data = response.json()
    return data.get('time')


if __name__ == '__main__':
    app.run()
