import etcd

from central.config.etcd import EtcdConfig

client = etcd.Client()

config = EtcdConfig(client, '/appname/config')
config.load()

print(config.get('database.host'))
print(config.get('database.port'))
