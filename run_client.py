from data_marketplace.client.api import client
from data_marketplace.utils.log import logging
from data_marketplace.utils.common import read_json
from data_marketplace.crypto.sha256 import get_digest

log = logging.getLogger('data_mareketplace.run_client')

if __name__ == '__main__':
 
   client.run()
   response = read_json('./data_marketplace/tx_templates/v1.0/s2_schema_response.json')
   client.registry('./_file/client/raw/20190611-11.log', response, 10, '2019-06-17')
   