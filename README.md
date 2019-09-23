# What is this?
This is just another URL scraper in Python

# Why?
This is a simple example of threadsafe use of requests, with retry, backoff, and support for user supplied headers.
It's simple enough to be easy to comprehend, but also exposes tunables and options for flexibility and seeing where the point of diminishing returns is for parallelized requests.

# Install
* `git clone` this repo.
* create a virtualenv: `virtualenv -p python3 venv`
* activate venv: `. ./venv/bin/activate`
* install requirements: `pip -r requirements.txt`
* run the program, as described in "usage"

# Usage
```
./scrape.py --help
usage: scrape.py [-h] [-f FILE] [-l LOGFILE] [-t THREADS] [-H HEADERS]
                 [--timeout TIMEOUT] [-d]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  file to read (list of URLs to scrape, default =>
                        list.txt)
  -l LOGFILE, --logfile LOGFILE
                        logfile to write (default => log.txt)
  -t THREADS, --threads THREADS
                        number fo threads to run
  -H HEADERS, --headers HEADERS
                        headers to pass to the worker, specified in json
                        format
  --timeout TIMEOUT     timeout for each request
  -d, --debug           enable debugging
```

The included list.txt is this [handy gist](https://gist.github.com/demersdesigns/4442cd84c1cc6c5ccda9b19eac1ba52b).
It can also be fun to use your personal browser history or bookmarks.