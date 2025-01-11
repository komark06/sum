"""This module provides a class to manage subprocesses."""

import multiprocessing
import queue
import time
from abc import abstractmethod
from typing import Callable

from src.data_loader import Summons
from src.executor import AbstractExecutor, BruteForceExecutor, Result


def _calculate(
    executor: BruteForceExecutor,
    queue: multiprocessing.Queue,
    targets: list[Summons],
    numbers: list[Summons],
    interval: float = 1.0,
):
    """Calculate all subset sum. Use as a child process."""
    start_time = time.time()

    def callback(progress: float):
        nonlocal start_time
        if time.time() - start_time > interval:
            queue.put(progress)
            start_time = time.time()
            print(progress * 100)

    return executor.calculate_all(targets, numbers, callback=callback)


class AbstractSubprocessManager:
    @abstractmethod
    def is_running(self):
        """Check if the subprocess is running."""

    @abstractmethod
    def terminate(self):
        """Terminate the subprocess."""

    @abstractmethod
    def start_calculation(
        self,
        executor: AbstractExecutor,
        targets: list[Summons],
        numbers: list[Summons],
        callback: Callable[[list[Result]], None],
        error_callback: Callable[[Exception], None],
        interval: float,
    ):
        """Start the calculation in a subprocess."""

    @abstractmethod
    def stop_calculation(self):
        """Stop the calculation and renew resources."""

    @abstractmethod
    def update_status(self):
        """Update the status of the calculation."""


class SubprocessManager:
    def __init__(self):
        self.async_result = None
        self.queue = multiprocessing.Manager().Queue()
        self.pool = multiprocessing.Pool()

    def terminate(self):
        """Terminate the subprocess."""
        self.pool.terminate()

    def is_running(self):
        """Check if the subprocess is running."""
        return self.async_result is not None and not self.async_result.ready()

    def start_calculation(
        self,
        executor: AbstractExecutor,
        targets: list[Summons],
        numbers: list[Summons],
        callback: Callable[[list[Result]], None] = lambda x: None,
        error_callback: Callable[[Exception], None] = lambda x: None,
        interval: float = 1.0,
    ):
        """Start the calculation in a subprocess."""
        self.async_result = self.pool.apply_async(
            _calculate,
            (executor, self.queue, targets, numbers, interval),
            callback=callback,
            error_callback=error_callback,
        )

    def stop_calculation(self):
        """Stop the calculation and renew resources."""
        self.pool.terminate()
        self.async_result = None
        self.pool = multiprocessing.Pool()
        self.queue = multiprocessing.Manager().Queue()

    def update_status(self):
        try:
            return self.queue.get_nowait()
        except queue.Empty:
            return None
