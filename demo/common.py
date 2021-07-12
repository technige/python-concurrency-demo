#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-


from abc import ABC, abstractmethod
from hashlib import sha3_512
from random import Random


class BaseService(ABC):
    """ A service that employs workers to process jobs.
    """

    def __init__(self, workers, jobs):
        self.workers = []
        for worker in workers:
            worker.service = self
            self.workers.append(worker)
        self.add_jobs(jobs)

    @abstractmethod
    def start(self):
        """ Start the service and all associated workers.
        """

    @abstractmethod
    def stop(self):
        """ Stop the service and all associated workers.
        """

    @abstractmethod
    def is_running(self):
        """ True if the service is running, false otherwise.
        """

    @abstractmethod
    def add_jobs(self, jobs):
        """ Add jobs to the workload queue.
        """

    @abstractmethod
    def get_job(self, timeout):
        """ Get the next job in the workload queue.
        """


class BaseWorker(ABC):
    """ A worker that processes jobs on behalf of a service.
    """

    def __init__(self, number):
        self.number = number
        self.service = None

    def __str__(self):
        return f"Worker #{self.number}"

    @abstractmethod
    def start(self):
        """ Start working.
        """

    @abstractmethod
    def stop(self):
        """ Stop working.
        """


class Job(ABC):
    """ A processable item of work.
    """

    @abstractmethod
    def process(self):
        """ Process the job.
        """


class CPUBoundJob(Job):
    """ A CPU-intensive item of work.
    """

    @classmethod
    def create_random_list(cls, size, seed=None):
        """ Create a list of CPU-bound jobs.
        """
        r = Random()
        r.seed(seed)
        jobs = []
        for n in range(size):
            size = 0.5 + r.random()
            jobs.append(CPUBoundJob(n, size))
        return jobs

    def __init__(self, number, size):
        self.number = number
        self.size = size

    def __str__(self):
        return f"Job #{self.number} (type=CPUBoundJob, size={self.size})"

    def process(self):
        for i in range(int(1000000 * self.size)):
            h = sha3_512()
            h.update(b"")
            _ = h.digest()
