from central.config.database import SQLAlchemyConfig
from sqlalchemy import create_engine

# initializes a in memory database
engine = create_engine('sqlite:///:memory:')
engine.execute('CREATE TABLE configurations (key TEXT PRIMARY KEY NOT NULL, value TEXT NOT NULL)')
engine.execute('INSERT INTO configurations VALUES ("database.host",  "localhost")')
engine.execute('INSERT INTO configurations VALUES ("database.port",  "1234")')

config = SQLAlchemyConfig(engine, 'select * from configurations')
config.load()

print(config.get('database.host'))
print(config.get('database.port'))
