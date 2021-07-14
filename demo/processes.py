#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-


from argparse import ArgumentParser
from logging import basicConfig, INFO, info

from multiprocessing import (Lock, Process, Queue,
                             current_process, get_all_start_methods, set_start_method)
from queue import Empty
from time import sleep

from .jobs import CPUBoundJob


class Service:
    """ A service that operates using process-based concurrency.
    """

    def __init__(self):
        self.run_lock = Lock()
        self.jobs = Queue()

    def __str__(self):
        return f"Service-{id(self)}"

    def add_jobs(self, jobs):
        """ Add jobs to the workload queue.
        """
        for job in jobs:
            self.jobs.put_nowait(job)

    def run(self, n_workers, timeout):
        """ Run the service with the given number of workers for the
        given number of seconds.
        """
        workers = []

        info(f"Starting {self}")
        self.run_lock.acquire()
        for _ in range(n_workers):
            worker = Process(target=self.work)
            worker.start()
            workers.append(worker)

        sleep(timeout)

        info(f"Stopping {self}")
        self.run_lock.release()
        for worker in workers:
            worker.join()

    def work(self):
        """ Worker method to continuously process jobs from the
        workload until the service stops running.

        This method is executed within the Process context, and will
        therefore run multiple times, concurrently. As logging is not
        supported across multiple processes in Python (see link below)
        then this is also explicitly configured here.

        (https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes)
        """
        basicConfig(level=INFO)
        me = current_process().name
        info(f"{me} is starting work")
        while is_locked(self.run_lock):
            try:
                job = self.jobs.get(timeout=1.0)
            except Empty:
                # A multiprocessing.Queue will raise a queue.Empty
                # exception if the get() call times out.
                info(f"{me} has no work to do")
            else:
                info(f"{me} is processing {job}")
                job.process()
                info(f"{me} has completed {job}")
        info(f"{me} has finished work")


def is_locked(lock):
    """ The multiprocessing.Lock class does not have a locked()
    method, so we simulate it here by trying to acquire the lock
    without blocking.
    """
    if lock.acquire(block=False):
        lock.release()
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
    service = Service()
    service.add_jobs(CPUBoundJob.create_random_list(args.jobs, seed=args.seed))
    service.run(n_workers=args.workers, timeout=args.time)


if __name__ == "__main__":
    basicConfig(level=INFO)
    main()
