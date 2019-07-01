import os
from data_marketplace.client.api import client
from data_marketplace.utils.log import logging
from data_marketplace.utils.common import read_json

log = logging.getLogger('data_mareketplace.run_client')

if __name__ == '__main__':
   print(os.path.dirname(os.path.abspath(__file__)))

   client.read_config('./instance/client/producer/producer.ini')
   client.run()

   response = read_json('./data_marketplace/tx_templates/v1.0/s2_schema_response.json')
   result = client.registry('./_file/client/raw/134217728.txt', response, 10, '2019-07-01')

   log.info('Data Registration Result: %s', result)
   client.shutdown()