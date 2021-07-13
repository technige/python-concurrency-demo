#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-


from asyncio import Lock, Queue, TimeoutError, create_task, run, sleep, wait_for
from logging import basicConfig, INFO, info

from .jobs import CPUBoundJob


class Service:
    """ A service that operates using coroutine-based concurrency.
    """

    def __init__(self, n_workers):
        self.run_lock = Lock()
        self.jobs = Queue()
        self.workers = [Worker(self.run_lock, self.jobs)
                        for _ in range(n_workers)]

    def add_jobs(self, jobs):
        for job in jobs:
            self.jobs.put_nowait(job)

    async def start(self):
        """ Start the service and all associated workers.
        """
        info(f"Starting {self}")
        await self.run_lock.acquire()
        for worker in self.workers:
            info(f"Starting {worker}")
            worker.start()

    async def stop(self):
        """ Stop the service and all associated workers.
        """
        info(f"Stopping {self}")
        self.run_lock.release()
        for worker in self.workers:
            info(f"Stopping {worker}")
            await worker.join()


class Worker:
    """ A worker that uses coroutines.

    Unlike with threads and processes, this doesn't extend a base class
    but instead embeds a Task object. This is because the Python manual
    recommends using the create_task function to create Tasks.
    """

    def __init__(self, run_lock, jobs):
        self.run_lock = run_lock
        self.jobs = jobs
        self.task = None

    def __repr__(self):
        if self.task:
            return f"<Worker({self.task.get_name()})>"
        else:
            return super().__repr__()

    async def work(self):
        """ Continuously process jobs from the service workload until
        the service stops running.
        """
        info(f"{self} is starting work")
        while self.run_lock.locked():
            try:
                job = await wait_for(self.jobs.get(), timeout=1.0)
            except TimeoutError:
                # An asyncio.Queue does not accept a timeout argument
                # for its get() method. So this is instead wrapped in
                # a wait_for() call, which will raise an
                # asyncio.TimeoutError exception if it times out.
                info(f"{self} has no work to do")
            else:
                info(f"{self} is processing {job}")
                job.process()
                info(f"{self} has completed {job}")
        info(f"{self} has finished work")

    def start(self):
        """ Start the worker by scheduling a task.
        """
        self.task = create_task(self.work())

    async def join(self):
        """ Wait for the task to complete.
        """
        await self.task


async def main():
    """ Create a service with four workers and run a list of
    100 cpu-bound jobs with a time limit of 10s.
    """
    service = Service(n_workers=4)
    service.add_jobs(CPUBoundJob.create_random_list(20, seed=0))
    await service.start()
    await sleep(10.0)
    await service.stop()


if __name__ == "__main__":
    basicConfig(level=INFO)
    run(main())
