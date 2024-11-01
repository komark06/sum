import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import combinations
from typing import Optional

from src.data_loader import AbstractDataLoader, ExcelDataLoader, Summons

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
        target (Summons): The target of subset sum problem.
        subset (Optional[List[Summons]]): The subset of Summons that
            sums up to the target. If no such subset exists, it is
            None.
    """

    target: Summons
    subset: Optional[list[Summons]]


class AbstractExecutor(ABC):
    data_loader: AbstractDataLoader

    @abstractmethod
    def calculate_all(
        self, interval_sec: int = DEFAULT_INTERVAL
    ) -> list[Result]:
        """Calculate all subset sum."""


class BruteForceExecutor(AbstractExecutor):

    def __init__(
        self,
        data_loader: AbstractDataLoader = ExcelDataLoader,
        filename=None,
    ):
        """Initialize data loader and use it to load data."""
        self.data_loader = data_loader()
        if filename:
            self.data_loader.load(filename)
        else:
            self.data_loader.load()

    def _calculate(self, target: Summons, interval_sec: int) -> Result:
        """Find subset sum that is equal to target."""
        numbers = [
            i for i in self.data_loader.numbers if i.amount <= target.amount
        ]
        total_calculation = 2 ** len(numbers)
        already_calculation = 0
        start_time = time.time()
        for r in range(1, len(numbers)):
            for combination in combinations(numbers, r):
                if sum([i.amount for i in combination]) == target.amount:
                    _logger.debug(
                        f"Target {target.amount}: "
                        f"{tuple(i.amount for i in combination)}"
                    )
                    return Result(target, combination)
                already_calculation += 1
                current_time = time.time()
                if current_time - start_time > interval_sec:
                    _logger.info(
                        f"Calculating {target.amount}, "
                        f"{already_calculation/total_calculation*100:.2f}%"
                    )
                    start_time = time.time()
        _logger.debug(f"Target {target.amount}: NO result.")
        return Result(target, None)

    def calculate_all(
        self, interval_sec: int = DEFAULT_INTERVAL
    ) -> list[Result]:
        """Calculate all subset sum."""
        results = []
        count = 0
        overall_start_time = time.time()
        for target in self.data_loader.targets:
            start_time = time.time()
            result = self._calculate(target, interval_sec)
            end_time = time.time()
            _logger.info(
                f"Target: {target.amount}, "
                f"elapsed time: {end_time - start_time:.3f} seconds."
            )
            results.append(result)
            if result.subset:
                for i in result.subset:
                    self.data_loader.numbers.remove(i)
            count = count + 1
        elapsed_time = time.time() - overall_start_time
        _logger.info(f"Total elapsed time: {elapsed_time:.3f} " "seconds.")
        return results
