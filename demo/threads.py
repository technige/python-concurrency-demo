#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-


from logging import basicConfig, INFO, info
from queue import Queue, Empty
from threading import Lock, Thread

from .common import BaseService, BaseWorker, CPUBoundTask


class Service(BaseService):
    """ A service that operates using thread-based concurrency.
    """

    def __init__(self, workers):
        super().__init__(workers)
        self.run_lock = Lock()
        self.todo = Queue()

    def set_running(self):
        self.run_lock.acquire()

    def set_not_running(self):
        self.run_lock.release()

    def is_running(self):
        return self.run_lock.locked()

    def add_tasks(self, tasks):
        for task in tasks:
            self.todo.put(task)

    def get_task(self):
        try:
            return self.todo.get()
        except Empty:
            return None


class Worker(BaseWorker):

    def __init__(self, number):
        super().__init__(number)
        self.thread = None

    def start(self):
        info(f"Starting {self}")
        self.thread = Thread(target=self.work)
        self.thread.start()

    def stop(self):
        info(f"Stopping {self}")
        self.thread.join()
        self.thread = None


if __name__ == "__main__":
    basicConfig(level=INFO)
    # Create a service with four workers and run a list of
    # 100 cpu-bound tasks with a time limit of 10s.
    (Service(Worker(n) for n in range(4))
     .run(CPUBoundTask.create_random_list(100, seed=0), timeout=10.0))
