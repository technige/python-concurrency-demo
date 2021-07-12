#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-


from logging import basicConfig, INFO, info
from multiprocessing import Process, Queue, Lock
# A multiprocessing.Queue can raise a queue.Empty exception
from queue import Empty

from .common import BaseService, BaseWorker, CPUBoundTask


class Service(BaseService):
    """ A service that operates using process-based concurrency.
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
        # The multiprocessing.Lock class does not have a
        # locked() method, so we simulate it.
        if self.run_lock.acquire(block=False):
            self.run_lock.release()
            return False
        else:
            return True

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
        self.process = None

    def start(self):
        info(f"Starting {self}")
        self.process = Process(target=self.work)
        self.process.start()

    def stop(self):
        info(f"Stopping {self}")
        self.process.join()
        self.process = None


if __name__ == "__main__":
    basicConfig(level=INFO)
    # Create a service with four workers and run a list of
    # 100 cpu-bound tasks with a time limit of 10s.
    (Service(Worker(n) for n in range(4))
     .run(CPUBoundTask.create_random_list(100, seed=0), timeout=10.0))
