#!/usr/bin/env python3
__author__ = 'csuttles'

import argparse
import logging
import json
import re
import requests
import subprocess as sp
import shlex
import threading
import time
from queue import Queue


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", help="file to read (list of URLs to scrape)", action='store', default='list.txt')
parser.add_argument("-l", "--logilfe", help="logfile to write", action='store', default='log.txt')
parser.add_argument("-t", "--threads", help="number fo threads to run", action='store', default=6)
parser.add_argument("-H", "--headers", help="headers to pass to the worker, specified in json format",
                    action='store', default='{"x-test": "ctlfish"}')
parser.add_argument("-d", "--debug", help="enable debugging", action='store_true')
args = parser.parse_args()


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.captureWarnings(True)
logger = logging.getLogger(__name__)


def main():
    starttime = time.time()
    print(args)
    if args.debug:
        logger.setLevel(logging.DEBUG)

    data = {}
    if args.headers:
        data['headers'] = json.loads(args.headers)
    data['logger'] = logger

    queue = Queue()

    with open(args.file) as infile:
        for url in infile:
            url = url.strip()
            logger.info(f'queuing {url}')
            queue.put(url)

    for x in range(args.threads):
        worker = Worker(queue, data)
        worker.name = f'agent {x}'
        worker.start()

    queue.join()
    logger.info(f'took {time.time() - starttime}')


class Worker(threading.Thread):

    def __init__(self, queue, data):
        threading.Thread.__init__(self)
        self.queue = queue
        self.logger = data['logger']
        self.s = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        self.s.mount('http://', adapter)
        self.s.mount('https://', adapter)
        self.s.headers.update(data['headers'])

    def run(self):
        while True:
            url = self.queue.get()
            try:
                resp = self.s.get(url, headers={'X-name': f'agent {self.name}'})
                logger.info(f'fetched {url} {resp.status_code}')
            except requests.exceptions.SSLError as err:
                logger.error(f'fetching {url} failed with SSL error: {err}')
                self.queue.task_done()
                break
            except requests.exceptions.ConnectionError as err:
                logger.error(f'fetching {url} failed with Connection error: {err}')
                self.queue.task_done()
                break
            finally:
                self.queue.task_done()
        self.s.close()


if __name__ == '__main__':
    main()
