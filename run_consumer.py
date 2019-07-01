import os
from data_marketplace.client.api import client
from data_marketplace.utils.log import logging
from data_marketplace.utils.common import read_json

log = logging.getLogger('data_mareketplace.run_client')

if __name__ == '__main__':
   print(os.path.dirname(os.path.abspath(__file__)))
   client.read_config('./instance/client/consumer/consumer.ini')
   client.run()
#    result = client.purchase('SRDFSAHDPDKMMIUSELLLZ9VNTEZLGNQRTSVSTFVUFGNLZNNGHSOQWUATXJRPCR9VLQHEPOSYKR9YGNGLBYYVODSYEX', \
#                             'BVIAWBP9WCALFUEZXJQLOC9AARPNSKDVZTOD9WCULDEBDWDFYRIEEIVZRSUJ9BKCPGJOQAVITKJFL9PUB', \
#                             10)
#    log.info('Data Purchase Result: %s', result)

   result = client.download('NH99BPTFCR9BJMEFJRKWGIW9C9FHUYKNDCAGAPDNCVSXDZQJJHBZETICTPATSXVZCKVMP9L9JMEYZ9999')
   log.info('Data Download Result: %s', result)

   client.sio.wait()