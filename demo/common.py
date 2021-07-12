#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-


from abc import ABC, abstractmethod
from hashlib import sha3_512
from logging import info
from random import Random
from time import monotonic


class BaseService(ABC):
    """ A service that employs workers to process tasks.
    """

    def __init__(self, workers):
        self.workers = []
        for worker in workers:
            worker.service = self
            self.workers.append(worker)

    def run(self, tasks, timeout):
        """ Run the service with a particular workload
        for a period of time.
        """
        self.add_tasks(tasks)
        t0 = monotonic()
        self.start()
        while monotonic() - t0 < timeout:
            pass
        self.stop()

    def start(self):
        """ Start the service and all associated workers.
        """
        info("Service starting")
        self.set_running()
        for worker in self.workers:
            worker.start()

    def stop(self):
        """ Stop the service and all associated workers.
        """
        info("Service stopping")
        self.set_not_running()
        for worker in self.workers:
            worker.stop()

    @abstractmethod
    def set_running(self):
        """ Mark the service as running.
        """

    @abstractmethod
    def set_not_running(self):
        """ Mark the service as not running.
        """

    @abstractmethod
    def is_running(self):
        """ True if the service is running, false otherwise.
        """

    @abstractmethod
    def add_tasks(self, tasks):
        """ Add tasks to the workload queue.
        """

    @abstractmethod
    def get_task(self):
        """ Get the next task in the workload queue.
        """


class BaseWorker(ABC):
    """ A worker that processes tasks on behalf of a service.
    """

    def __init__(self, number):
        self.number = number
        self.service = None

    def __str__(self):
        return f"Worker #{self.number}"

    def work(self):
        """ Continuously process tasks from the service workload until
        either the service stops running or the workload is empty.

        This method is used as a callback after the worker has been
        started.
        """
        info(f"{self} is starting work")
        while self.service.is_running():
            task = self.service.get_task()
            if task:
                info(f"{self} is processing {task}")
                task.process()
                info(f"{self} has completed {task}")
            else:
                break
        info(f"{self} has finished work")

    @abstractmethod
    def start(self):
        """ Start working.
        """

    @abstractmethod
    def stop(self):
        """ Stop working.
        """


class Task(ABC):
    """ A processable item of work.
    """

    @abstractmethod
    def process(self):
        """ Process the task.
        """


class CPUBoundTask(Task):
    """ A CPU-intensive item of work.
    """

    @classmethod
    def create_random_list(cls, size, seed=None):
        """ Create a list of CPU-bound tasks.
        """
        r = Random()
        r.seed(seed)
        tasks = []
        for n in range(size):
            size = 0.5 + r.random()
            tasks.append(CPUBoundTask(n, size))
        return tasks

    def __init__(self, number, size):
        self.number = number
        self.size = size

    def __str__(self):
        return f"CPUBoundTask #{self.number} (size={self.size})"

    def process(self):
        for i in range(int(1000000 * self.size)):
            h = sha3_512()
            h.update(b"")
            _ = h.digest()
