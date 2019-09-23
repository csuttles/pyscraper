#!/usr/bin/env python3
__author__ = 'csuttles'

import argparse
import logging
import json
import requests
import sys
import threading
import time
from queue import Queue
from requests.packages.urllib3.util.retry import Retry

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", help="file to read (list of URLs to scrape, default => list.txt)", action='store', default='list.txt')
parser.add_argument("-l", "--logfile", help="logfile to write (default => log.txt)", action='store', default='log.txt')
parser.add_argument("-t", "--threads", help="number fo threads to run", action='store', default=6, type=int)
parser.add_argument("-H", "--headers", help="headers to pass to the worker, specified in json format",
                    action='store', default='{"x-test": "ctlfish"}')
parser.add_argument("--timeout", action='store', help="timeout for each request", default=1, type=int)
parser.add_argument("-d", "--debug", help="enable debugging", action='store_true')
args = parser.parse_args()


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.captureWarnings(True)
logger = logging.getLogger(__name__)


def main():
    starttime = time.time()
    if args.logfile:
        fh = logging.FileHandler(args.logfile)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(fh)

    if args.debug:
        logger.setLevel(logging.DEBUG)
    logger.debug(f'invoked with {args}')

    data = {}
    if args.headers:
        data['headers'] = json.loads(args.headers)
    data['logger'] = logger
    data['timeout'] = args.timeout


    retry = Retry(
        total=3,
        read=3,
        connect=3,
        backoff_factor=0.3,
        status_forcelist=None,
    )
    data['retry'] = retry

    queue = Queue()

    for x in range(args.threads):
        worker = Worker(queue, data)
        worker.name = f'agent {x}'
        worker.daemon = True
        worker.start()

    with open(args.file) as infile:
        for url in infile:
            url = url.strip()
            logger.info(f'queuing {url}')
            queue.put(url)
    queue.join()
    logger.info(f'took {time.time() - starttime}')
    sys.exit(0)


class Worker(threading.Thread):

    def __init__(self, queue, data):
        threading.Thread.__init__(self)
        self.queue = queue
        self.logger = data['logger']
        self.s = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=data['retry'])
        self.s.mount('http://', adapter)
        self.s.mount('https://', adapter)
        self.s.headers.update(data['headers'])
        self.timeout = data['timeout']

    def run(self):
        while True:
            url = self.queue.get()
            try:
                resp = self.s.get(url, headers={'X-name': f'agent {self.name}'}, timeout=self.timeout)
                logger.info(f'{self.name} fetched {url} {resp.status_code}')
            except requests.exceptions.SSLError as err:
                logger.error(f'{self.name} fetching {url} failed with SSL error: {err}')
            except requests.exceptions.ConnectionError as err:
                logger.error(f'{self.name} fetching {url} failed with Connection error: {err}')
            finally:
                self.queue.task_done()


if __name__ == '__main__':
    main()
