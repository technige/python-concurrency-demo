#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-


from abc import ABC, abstractmethod
from hashlib import sha3_512
from random import Random


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
