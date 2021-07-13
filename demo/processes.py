#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-


from argparse import ArgumentParser
from logging import basicConfig, INFO, info
from multiprocessing import Lock, Process, Queue, get_all_start_methods, set_start_method
from queue import Empty
from time import sleep

from .jobs import CPUBoundJob


class Service:
    """ A service that operates using process-based concurrency.
    """

    def __init__(self, n_workers):
        self.run_lock = Lock()
        self.jobs = Queue()
        self.workers = [Worker(self.run_lock, self.jobs)
                        for _ in range(n_workers)]

    def add_jobs(self, jobs):
        for job in jobs:
            self.jobs.put_nowait(job)

    def start(self):
        info(f"Starting {self}")
        self.run_lock.acquire()
        for worker in self.workers:
            info(f"Starting {worker}")
            worker.start()

    def stop(self):
        info(f"Stopping {self}")
        self.run_lock.release()
        for worker in self.workers:
            info(f"Stopping {worker}")
            worker.join()


class Worker(Process):
    """ A worker process.
    """

    def __init__(self, run_lock, jobs):
        self.run_lock = run_lock
        self.jobs = jobs
        super().__init__()

    def run(self):
        """ Continuously process jobs from the service workload until
        the service stops running.

        This method sets logging configuration so that logging is
        configured within the process itself. This is because logging
        across multiple processes is not supported in Python.

        (https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes)
        """
        basicConfig(level=INFO)
        info(f"{self} is starting work")
        while self.run_locked():
            try:
                job = self.jobs.get(timeout=1.0)
            except Empty:
                # A multiprocessing.Queue will raise a queue.Empty
                # exception if the get() call times out.
                info(f"{self} has no work to do")
            else:
                info(f"{self} is processing {job}")
                job.process()
                info(f"{self} has completed {job}")
        info(f"{self} has finished work")

    def run_locked(self):
        """ The multiprocessing.Lock class does not have a locked()
        method, so we simulate it here by trying to acquire the lock
        without blocking.
        """
        if self.run_lock.acquire(block=False):
            self.run_lock.release()
            return False
        else:
            return True


def main():
    """ Create and run a demo service to demonstrate concurrency using
    processes.
    """
    parser = ArgumentParser(description=main.__doc__)
    parser.add_argument("--jobs", type=int, default=20, help="number of jobs")
    parser.add_argument("--method", choices=get_all_start_methods(), default=None,
                        help="method to start child processes")
    parser.add_argument("--seed", type=int, default=None, help="random seed")
    parser.add_argument("--time", type=float, default=10.0, help="time to run (seconds)")
    parser.add_argument("--workers", type=int, default=4, help="number of workers")
    args = parser.parse_args()
    #
    # Child processes can be created using one of several available
    # methods, depending on the platform. This sets that method or,
    # if set to None, uses the default for the OS.
    set_start_method(args.method)
    #
    service = Service(n_workers=args.workers)
    service.add_jobs(CPUBoundJob.create_random_list(args.jobs, seed=args.seed))
    service.start()
    sleep(args.time)
    service.stop()


if __name__ == "__main__":
    basicConfig(level=INFO)
    main()
