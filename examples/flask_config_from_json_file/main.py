from central.config import FileConfig
from flask import Flask

config = FileConfig('config.json')
config.load()

app = Flask(__name__)
app.config.from_mapping(config)

print(app.config.get('DEBUG'))
print(app.config.get('SECRET_KEY'))
