import json
from iota import Iota
from data_marketplace.utils.log import logging
from data_marketplace.utils.common import print_json

log = logging.getLogger('data_marketplace.utils.iota')


def connect_iota(nodes, seed):
   log.info('Connecting IOTA network. IOTA full node list: %s', nodes)
   connected = False
   times = 1
   node = nodes.pop()
   while not connected:
      try:
         log.info(
             'Trying to connecting IOTA node. Node address: "%s" Times: %d',
             node, times)
         iota = Iota(node, seed)
         info = iota.get_node_info()
         connected = True
         log.info('Success Connected to IOTA node. Node address: "%s"\n'\
                  'Node Information:\n %s', node, print_json(info))
      except:
         if times < 3:
            times += 1
         else:
            try:
               node = nodes.pop()
            except IndexError:
               raise ConnectionError
         log.error('IOTA Connection Error. Retry Again.', exc_info=True)
   return iota

def get_tx_ctx(node, tx_hash):
   bundle = node.get_bundles(tx_hash)['bundles'][0]
   tx = bundle.transactions[0]
   tx_sig = bundle.transactions[1]
   msg = json.loads(tx.signature_message_fragment.as_string())
   sig = json.loads(tx_sig.signature_message_fragment.as_string())

   return (msg, sig)