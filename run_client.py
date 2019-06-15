from data_marketplace.client.api import client
from data_marketplace.utils.log import logging

log = logging.getLogger('data_mareketplace.main')

if __name__ == '__main__':
   client.run()
   client.registry('./_file/client/raw/20190611-11.log')
   