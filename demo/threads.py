from logging import basicConfig, INFO, info
from queue import Queue, Empty
from random import random
from threading import Lock, Thread
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
        return self.run_lock.locked()

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
        self.thread = None

    def start(self, service):
        info(f"Starting {self}")
        super().start(service)
        self.thread = Thread(target=self.work)
        self.thread.start()

    def stop(self):
        info(f"Stopping {self}")
        self.thread.join()
        self.thread = None


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
