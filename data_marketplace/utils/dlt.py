import time
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
   return _extract(bundle)

def get_tx_ctx_by_bundle(node, bundle_hash):
   txs = node.findTransactions(bundles = [bundle_hash])['hashes']
   idx = 0
   status = False
   while not status:
      try:
         bundle = node.get_bundles(txs[idx])['bundles'][0]
         msg, sig = _extract(bundle)
         status = True
      except node.adapter.BadApiResponse:
         if idx < len(txs):
            idx += 1 
         else:
            status = True
            raise Exception('Fail to get Tx from Bundle Hash')

   return (msg, sig)

def _extract(bundle):
   tx = bundle.transactions[0]
   tx_sig = bundle.transactions[1]
   msg = json.loads(tx.signature_message_fragment.as_string())
   sig = json.loads(tx_sig.signature_message_fragment.as_string()) 

   return (msg, sig)

def check_bundle_confirmed(node, bundle_hash):
   txs = node.findTransactions(bundles = [bundle_hash])['hashes']
   states = node.get_latest_inclusion(hashes=txs)['states'].values()
   return any(states)

def check_tx_confirmed(node, tx_hash):
   states = node.get_latest_inclusion([tx_hash])['states']
   return all(states.values())

def wait_tx_confirmed(node, tx_hash, wait_interval, callback):
   log.info('Start waiting Tx [%s] to be confirmed at timestamp %d',
            tx_hash, time.time())
   result = False
   while not result:
      result = check_tx_confirmed(node, tx_hash)
      if result is False:
         time.sleep(wait_interval)
         log.info('Still waiting Tx [%s] to be confirmed at timestamp %d',
                  tx_hash, time.time())
   callback()

if __name__ == "__main__":
   node = Iota('https://nodes.thetangle.org:443')
   bundle = get_tx_by_bundle(node, 'BVIAWBP9WCALFUEZXJQLOC9AARPNSKDVZTOD9WCULDEBDWDFYRIEEIVZRSUJ9BKCPGJOQAVITKJFL9PUB')
   print(bundle)
