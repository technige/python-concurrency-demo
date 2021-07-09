from abc import ABC, abstractmethod
from hashlib import sha3_512
from logging import info


class BaseService(ABC):

    def __init__(self):
        self.workers = []

    def add_worker(self, worker):
        self.workers.append(worker)

    def start(self):
        info("Service starting")
        self.set_running()
        for worker in self.workers:
            worker.start(self)

    def stop(self):
        info("Service stopping")
        self.set_not_running()
        for worker in self.workers:
            worker.stop()

    @abstractmethod
    def set_running(self):
        raise NotImplementedError

    @abstractmethod
    def set_not_running(self):
        raise NotImplementedError

    @abstractmethod
    def is_running(self):
        raise NotImplementedError

    @abstractmethod
    def add_task(self, task):
        raise NotImplementedError

    @abstractmethod
    def get_task(self):
        raise NotImplementedError


class BaseWorker(ABC):

    def __init__(self, number):
        self.number = number
        self.service = None

    def __repr__(self):
        return f"Worker(number={self.number})"

    def work(self):
        info(f"{self} is starting work")
        while self.service.is_running():
            task = self.service.get_task()
            if task:
                info(f"{self} is processing {task}")
                task.process()
            else:
                break
        info(f"{self} has finished work")

    @abstractmethod
    def start(self, service):
        self.service = service

    @abstractmethod
    def stop(self):
        pass


class Task:

    def __init__(self, number, size):
        self.number = number
        self.size = size

    def __repr__(self):
        return f"Task(number={self.number}, size={self.size})"

    def process(self):
        for i in range(int(1000000 * self.size)):
            h = sha3_512()
            h.update(b"")
            _ = h.digest()
