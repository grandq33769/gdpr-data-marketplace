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
#                             'QYZIKFIA9EYYEXT9UZO99OMMRABZPHQDQXFFEFDXUKYHXHPZOHOMCMTUQDM9JAXXWMYLZFLKLPXBA9999', \
#                             10)
#    log.info('Data Purchase Result: %s', result)

#    result = client.download('SVGSLYLZURZWFLKFLXDEHKXEXHUSEBTZHDMHXSCEGPTGABUBUKHUY9LZWGOLFCKKCG9H9WJDTTCPZ9999')
   result = client.download('EFLCIDVYIDZOLDUAHFWEVVHDBKEEIXBPEGDYQKJQ9CEWTKTODRWMSCMCNGBHDCKC9POZCKKQEOZNZ9999')
   log.info('Data Download Result: %s', result)