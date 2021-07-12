#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-


from asyncio import Lock, Queue, QueueEmpty, create_task, run, wait_for, sleep
from logging import basicConfig, INFO, info

from .common import BaseService, BaseWorker, CPUBoundJob


class Service(BaseService):
    """ A service that operates using coroutine-based concurrency.
    """

    def __init__(self, workers, jobs):
        self.run_lock = Lock()
        self.todo = Queue()
        super().__init__(workers, jobs)

    async def start(self):
        """ Start the service and all associated workers.
        """
        info("Service starting")
        await self.run_lock.acquire()
        for worker in self.workers:
            worker.start()

    async def stop(self):
        """ Stop the service and all associated workers.
        """
        info("Service stopping")
        self.run_lock.release()
        for worker in self.workers:
            await worker.stop()

    def is_running(self):
        return self.run_lock.locked()

    def add_jobs(self, jobs):
        for job in jobs:
            self.todo.put_nowait(job)

    async def get_job(self, timeout):
        try:
            return await wait_for(self.todo.get(), timeout=timeout)
        except QueueEmpty:
            raise IndexError("No more jobs")


class Worker(BaseWorker):
    """ A worker that uses coroutines.
    """

    def __init__(self, number):
        super().__init__(number)
        self.task = None

    async def work(self):
        """ Continuously process jobs from the service workload until
        the service stops running.

        This method is used as a callback after the worker has been
        started.
        """
        info(f"{self} is starting work")
        while self.service.is_running():
            try:
                job = await self.service.get_job(timeout=1.0)
            except IndexError:
                info(f"{self} has no work to do")
            else:
                info(f"{self} is processing {job}")
                job.process()
                info(f"{self} has completed {job}")
        info(f"{self} has finished work")

    def start(self):
        info(f"Starting {self}")
        self.task = create_task(self.work())

    async def stop(self):
        info(f"Stopping {self}")
        await self.task


async def main():
    """ Create a service with four workers and run a list of
    100 cpu-bound jobs with a time limit of 10s.
    """
    service = Service([Worker(n) for n in range(4)],
                      CPUBoundJob.create_random_list(100, seed=0))
    await service.start()
    await sleep(10.0)
    await service.stop()


if __name__ == "__main__":
    basicConfig(level=INFO)
    run(main())
