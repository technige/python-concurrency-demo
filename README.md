# Python Concurrency Demo

This repository is a demo of how to implement concurrency in Python applications.
Python 3.8 or above is required to run the code, which is exposed as modules
that can be executed from the command line.

Each executable module runs a service comprised of a number of workers running
a number of randomly-generated jobs. Each job is CPU-bound, and workers pick
jobs in succession from a shared queue. 

There are three methods of concurrency implemented, which demonstrate the three
basic types of concurrency available to Python applications: threads, processes, 
and coroutines. Each of these methods has trade-offs against the others, and
all are implemented here using a very similar structure in order to highlight
the differences. It is highly recommended to read the code to understand how
each works.

**Note: the three forms of concurrency highlighted here are not generally
compatible with each other. While some overlap exists in places, it is
recommended to stick to a single method per application.**

Several command line options are available to fine tune the behaviour of the modules:

- `--jobs=N` - set the number of jobs on the shared queue (default=20)
- `--seed=N` - set a random seed allowing jobs to be similar across runs
- `--time=N` - set the number of seconds for which the service should run (default=10)
- `--workers=N` - set the number of workers available to the service (default=4)


## The Global Interpreter Lock (GIL)

> In CPython, the global interpreter lock, or GIL, is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecodes at once.
>
> -- <cite>https://wiki.python.org/moin/GlobalInterpreterLock</cite>

Due to the presence of the GIL in CPython, there are significant differences
between the various forms of concurrency available. Thread-based concurrency
will not generally speed up CPU-bound workloads since each Python process allows
only one piece of bytecode to be executing at any given moment.

Multiple processes can therefore be used to avoid the GIL, but come with other
challenges, wherein [objects cannot be trivially exchanged between processes](https://docs.python.org/3/library/multiprocessing.html#exchanging-objects-between-processes). 


## Synchronization primitives

Each demo module uses a `Lock` object which is locked while the service is running.
Due to incompatibilities across the methods of concurrency, however, three different
`Lock` classes are available in Python: `threading.Lock`, `multiprocessing.Lock` and
`asyncio.Lock`. It is important to be aware of which of these should be used for any
given scenario.

The semantics of each `Lock` class are similar, but the `multiprocessing.Lock` class
is missing a `locked()` method which the code here simulates.

Each of the three standard library modules mentioned above also provides a number of
other synchronization primitives, such as _Conditions_, _Events_ and _Semaphores_.
Again, these are not compatible across concurrency methods.


# Queues

Each Python concurrency module also has a different implementation available for managing
a queue: `queue.Queue` (for threading), `multiprocessing.Queue` and `asyncio.Queue`.
The semantics of each are similar, but differ slightly. For example, the `asyncio.Queue`
does not accept a `timeout` argument, relying instead on the `asyncio.wait_for` function.


## Thread-based concurrency

To run the threading demo, use:
```shell script
$ python -m demo.threads
```

## Process-based concurrency

To run the multiprocessing demo, use:
```shell script
$ python -m demo.processes
```

The process-based concurrency demo accepts a further command line option `--method`
to set the start method for child processes. The value can be either `fork`, 
`spawn` or `forkserver` and the default differs by operating system. For more
information, look at the [Python documentation](https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods).


## Coroutine-based concurrency

To run the coroutines demo, use:
```shell script
$ python -m demo.coroutines
```
