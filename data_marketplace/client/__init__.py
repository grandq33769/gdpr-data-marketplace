import os
import socketio
from os.path import join
from argparse import ArgumentParser
from configparser import ConfigParser
from data_marketplace.utils.log import logging
from data_marketplace.client.app import DataMarketplaceClient

now = os.path.dirname(os.path.abspath(__file__))

sio = socketio.Client()
config = ConfigParser()
config.read(join(now, '../../config/client/default.ini'))
config.read(join(now, '../../instance/client/secrete.ini'))
client = DataMarketplaceClient(config, sio)
