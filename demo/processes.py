#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-


from logging import basicConfig, INFO, info
from multiprocessing import Lock, Process, Queue
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
    """ Create a service with four workers and run a list of
    100 cpu-bound jobs with a time limit of 10s.
    """
    service = Service(n_workers=4)
    service.add_jobs(CPUBoundJob.create_random_list(20, seed=0))
    service.start()
    sleep(10.0)
    service.stop()


if __name__ == "__main__":
    basicConfig(level=INFO)
    main()
