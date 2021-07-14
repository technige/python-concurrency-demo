#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-


from argparse import ArgumentParser
from logging import basicConfig, INFO, info

from queue import Queue, Empty
from threading import Lock, Thread, current_thread
from time import sleep

from .jobs import CPUBoundJob


class Service:
    """ A service that operates using thread-based concurrency.
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
            worker = Thread(target=self.work)
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

        This method is executed within the Thread context, and will
        therefore run multiple times, concurrently.
        """
        me = current_thread().name
        info(f"{me} is starting work")
        while self.run_lock.locked():
            try:
                job = self.jobs.get(timeout=1.0)
            except Empty:
                # A queue.Queue will raise a queue.Empty exception if
                # the get() call times out.
                info(f"{me} has no work to do")
            else:
                info(f"{me} is processing {job}")
                job.process()
                info(f"{me} has completed {job}")
        info(f"{me} has finished work")


def main():
    """ Create and run a demo service to demonstrate concurrency using
    threads.
    """
    parser = ArgumentParser(description=main.__doc__)
    parser.add_argument("--jobs", type=int, default=20, help="number of jobs")
    parser.add_argument("--seed", type=int, default=None, help="random seed")
    parser.add_argument("--time", type=float, default=10.0, help="time to run (seconds)")
    parser.add_argument("--workers", type=int, default=4, help="number of workers")
    args = parser.parse_args()
    #
    service = Service()
    service.add_jobs(CPUBoundJob.create_random_list(args.jobs, seed=args.seed))
    service.run(n_workers=args.workers, timeout=args.time)


if __name__ == "__main__":
    basicConfig(level=INFO)
    main()
