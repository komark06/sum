from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import combinations
from typing import Optional

from src.data_loader import AbstractDataLoader, ExcelDataLoader, Summons


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

    def _calculate(self, target: Summons):
        """Find subset sum that is equal to target."""
        numbers = [
            i for i in self.data_loader.numbers if i.amount <= target.amount
        ]
        cal = 0
        for r in range(1, len(numbers)):
            for combination in combinations(numbers, r):
                if sum([i.amount for i in combination]) == target.amount:
                    return Result(target, combination)
                cal = cal + 1
        return Result(target, None)

    def calculate_all(self) -> list[Result]:
        results = []
        count = 0
        for target in self.data_loader.targets:
            result = self._calculate(target)
            results.append(result)
            if result.subset:
                for i in result.subset:
                    self.data_loader.numbers.remove(i)
            count = count + 1
        return results
