import socketio
from configparser import ConfigParser
from data_marketplace.utils.log import logging
from data_marketplace.client.app import DataMarketplaceClient

sio = socketio.Client()
config = ConfigParser()
config.read('config/client/default.ini')
config.read('instance/client/secrete.ini')
client = DataMarketplaceClient(config, sio)
