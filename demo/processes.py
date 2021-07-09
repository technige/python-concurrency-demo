from logging import basicConfig, INFO, info
from multiprocessing import Process, Queue, Lock
# A multiprocessing.Queue can raise a queue.Empty exception
from queue import Empty
from random import random
from time import monotonic

from .common import BaseService, BaseWorker, Task


class Service(BaseService):

    def __init__(self):
        super().__init__()
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

    def add_task(self, task):
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

    def start(self, service):
        info(f"Starting {self}")
        super().start(service)
        self.process = Process(target=self.work)
        self.process.start()

    def stop(self):
        info(f"Stopping {self}")
        self.process.join()
        self.process = None


def main():
    basicConfig(level=INFO)
    service = Service()
    for n in range(100):
        size = 0.5 + random()
        service.add_task(Task(n, size))
    for n in range(4):
        service.add_worker(Worker(n))

    t0 = monotonic()
    service.start()
    while monotonic() - t0 < 10.0:
        pass
    service.stop()


if __name__ == "__main__":
    main()
