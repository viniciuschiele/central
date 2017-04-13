from central.config.sqlalchemy import SQLAlchemyConfig
from sqlalchemy import create_engine

# initializes a in memory database
engine = create_engine('sqlite:///:memory:')
engine.execute('CREATE TABLE configs (key TEXT PRIMARY KEY NOT NULL, value TEXT NOT NULL)')
engine.execute('INSERT INTO configs VALUES ("database.host",  "localhost")')
engine.execute('INSERT INTO configs VALUES ("database.port",  "1234")')

config = SQLAlchemyConfig(engine, 'select * from configs')
config.load()

print(config.get('database.host'))
print(config.get('database.port'))
