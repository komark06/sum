import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import combinations
from typing import Optional

from src.data_loader import AbstractDataLoader, ExcelDataLoader, Summons

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


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
    def _calculate(self, target: Summons):
        """Calculate a subset sum."""

    @abstractmethod
    def calculate_all(self):
        """Calculate all subset sum."""


class BruteForceExecutor(AbstractExecutor):
    def __init__(self, data_loader: AbstractDataLoader = ExcelDataLoader):
        """Initialize data loader and use it to load data."""
        self.data_loader = data_loader()
        self.data_loader.load()

    def _calculate(self, target: Summons, interval_sec: int):
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
                    logger.debug(
                        f"Target {target.amount}: "
                        f"{tuple(i.amount for i in combination)}"
                    )
                    return Result(target, combination)
                already_calculation += 1
                current_time = time.time()
                if current_time - start_time > interval_sec:
                    logger.info(
                        f"Calculating {target.amount}, "
                        f"{already_calculation/total_calculation*100:.2f}%"
                    )
                    start_time = time.time()
        logger.debug(f"Target {target.amount}: NO result.")
        return Result(target, None)

    def calculate_all(self, interval_sec: int = 1) -> list[Result]:
        results = []
        count = 0
        start_time = time.time()
        for target in self.data_loader.targets:
            result = self._calculate(target, interval_sec)
            results.append(result)
            if result.subset:
                for i in result.subset:
                    self.data_loader.numbers.remove(i)
            count = count + 1
        elpased_time = time.time() - start_time
        logger.info(f"elpased time: {elpased_time:.3f} seconds.")
        return results
