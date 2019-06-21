import os
from data_marketplace.client.api import client
from data_marketplace.utils.log import logging
from data_marketplace.utils.common import read_json

log = logging.getLogger('data_mareketplace.run_client')

if __name__ == '__main__':
   print(os.path.dirname(os.path.abspath(__file__)))
   client.run()
   response = read_json('./data_marketplace/tx_templates/v1.0/s2_schema_response.json')
#    result = client.registry('./_file/client/raw/hello_world.csv', response, 10, '2019-06-17')
#    result = client.registry('./_file/client/raw/hello_world.csv', response, 10, '2019-06-18')
   result = client.registry('./_file/client/raw/67108864.txt', response, 10, '2019-06-18')
   log.info('Data Registraion Result: %s', result)
   client.shutdown()
   