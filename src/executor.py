"""This module contains executors that solve problems."""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Optional

from src.data_loader import Summons

_logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

DEFAULT_INTERVAL = 3


@dataclass
class Result:
    """
    Represents the result of a subset sum problem.

    Attributes:
        target: The target of subset sum problem.
        subset: The subset of Summons that
            sums up to the target. If no such subset exists, it is
            None.
    """

    target: Summons
    subset: Optional[list[Summons]]


class AbstractExecutor(ABC):
    """
    Abstract executor class that solve subset sum problem.
    """

    def __init__(self):
        self._init_status()

    def _init_status(self):
        """Initialize the status of the executor."""
        self._total_calculation = 0
        self._already_calculation = 0

    @abstractmethod
    def calculate_all(
        self,
        targets: list[Summons],
        numbers: list[Summons],
        callback: Callable[[float], None] = lambda x: None,
    ) -> list[Result]:
        """Calculate all subset sum.

        Parameters:
            targets: The list of targets.
            numbers: The subset that we search for the sum
                of its subset is equal to target.
            callback: A callback function that is called with the
                progress of the calculation. Defaults to a no-op lambda
                function.
        """


class BruteForceExecutor(AbstractExecutor):
    """
    Executor that use brute-force to solve subset sum problem.
    """

    def _calculate(
        self,
        target: Summons,
        numbers: list[Summons],
        callback: Callable[[float], None] = lambda x: None,
    ) -> Result:
        """Find subset sum that is equal to target.

        Parameters:
            target: The target that we want to solve.
            numbers: The subset where we search for the sum
                of its subset is equal to target.
            callback: A callback function that is called with the
                progress of the calculation. Defaults to a no-op lambda
                function.
        """
        numbers = [i for i in numbers if i.amount <= target.amount]
        for r in range(1, len(numbers)):
            for combination in combinations(numbers, r):
                total_amount = sum([i.amount for i in combination])
                self._already_calculation += 1
                callback(self._already_calculation / self._total_calculation)
                if total_amount == target.amount:
                    return Result(target, combination)
        return Result(target, None)

    def calculate_all(
        self,
        targets: list[Summons],
        numbers: list[Summons],
        callback: Callable[[float], None] = lambda x: None,
    ) -> list[Result]:
        self._init_status()
        self._total_calculation = 2 ** len(numbers)
        results = []
        count = 0
        _numbers = list(numbers)
        overall_start_time = time.time()
        for target in targets:
            start_time = time.time()
            result = self._calculate(target, numbers, callback)
            end_time = time.time()
            _logger.info(
                f"Target: {target.amount}, "
                f"elapsed time: {end_time - start_time:.3f} seconds."
            )
            results.append(result)
            if result.subset:
                for i in result.subset:
                    _numbers.remove(i)
            count = count + 1
        elapsed_time = time.time() - overall_start_time
        _logger.info(f"Total elapsed time: {elapsed_time:.3f} seconds.")
        return results
