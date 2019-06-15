import queue
from time import time, sleep
from threading import Thread
from data_marketplace.utils.log import logging

log = logging.getLogger('data_marketplace.thread')

def execute(que, func, *args):
   que.put(func(*args))

class DMthread():
   def __init__(self):
      self.que = queue.Queue()

   def run(self, func, *args):
      name = func.__name__

      t = Thread(target=execute,
                 args=(self.que, func, *args))
      t.start()
      log.info('Start %s()', name)
      while t.is_alive():
         log.info('Running %s() at timestamp %d ', name, time())
         sleep(1)
      t.join()
      log.info('Finish %s()', name)
      return self.que.get()
