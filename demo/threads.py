#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-


from logging import basicConfig, INFO, info
from queue import Queue, Empty
from threading import Lock, Thread
from time import sleep

from .common import BaseService, BaseWorker, CPUBoundJob


class Service(BaseService):
    """ A service that operates using thread-based concurrency.
    """

    def __init__(self, workers, jobs):
        self.run_lock = Lock()
        self.todo = Queue()
        super().__init__(workers, jobs)

    def start(self):
        info("Service starting")
        self.run_lock.acquire()
        for worker in self.workers:
            worker.start()

    def stop(self):
        info("Service stopping")
        self.run_lock.release()
        for worker in self.workers:
            worker.stop()

    def is_running(self):
        return self.run_lock.locked()

    def add_jobs(self, jobs):
        for job in jobs:
            self.todo.put_nowait(job)

    def get_job(self, timeout):
        try:
            return self.todo.get(timeout=timeout)
        except Empty:
            raise IndexError("No more jobs")


class Worker(BaseWorker):
    """ A worker that maintains its own thread.
    """

    def __init__(self, number):
        super().__init__(number)
        self.thread = None

    def work(self):
        """ Continuously process jobs from the service workload until
        the service stops running.

        This method is used as a target by the worker thread.
        """
        info(f"{self} is starting work")
        while self.service.is_running():
            try:
                job = self.service.get_job(timeout=1.0)
            except IndexError:
                info(f"{self} has no work to do")
            else:
                info(f"{self} is processing {job}")
                job.process()
                info(f"{self} has completed {job}")
        info(f"{self} has finished work")

    def start(self):
        info(f"Starting {self}")
        self.thread = Thread(target=self.work)
        self.thread.start()

    def stop(self):
        info(f"Stopping {self}")
        self.thread.join()


def main():
    """ Create a service with four workers and run a list of
    100 cpu-bound jobs with a time limit of 10s.
    """
    service = Service([Worker(n) for n in range(4)],
                      CPUBoundJob.create_random_list(20, seed=0))
    service.start()
    sleep(10.0)
    service.stop()


if __name__ == "__main__":
    basicConfig(level=INFO)
    main()
