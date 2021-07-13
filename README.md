# Python Concurrency Demo

This repository is a demo of how to implement concurrency in Python applications.
Python 3.8 or above is required to run the code.

To run the threading demo:
```shell script
$ python -m demo.threads
```

To run the multiprocessing demo:
```shell script
$ python -m demo.processes
```

To run the coroutines demo:
```shell script
$ python -m demo.coroutines
```

Each of the demo modules can also accept command line arguments used to fine tune the demo:
```shell script
$ python -m demo.processes --help
usage: threads.py [-h] [--jobs JOBS] [--seed SEED] [--time TIME] [--workers WORKERS]

Create and run a demo service to demonstrate concurrency using threads.

optional arguments:
  -h, --help         show this help message and exit
  --jobs JOBS        number of jobs
  --seed SEED        random seed
  --time TIME        time to run (seconds)
  --workers WORKERS  number of workers
```
