import datetime

from src.data_loader import AbstractDataLoader, Summons
from src.executor import BruteForceExecutor

numbers = [i for i in range(23)]
targets = [sum(numbers) + 1, numbers[-1]]


class FakeDataLoader(AbstractDataLoader):
    """A Fake Data Loader."""

    def __init__(self):
        super().__init__()
        self.targets = [
            Summons("targets", datetime.date(2020, 1, 1), target)
            for target in targets
        ]
        self.numbers = [
            Summons("numbers", datetime.date(2020, 1, 1), number)
            for number in numbers
        ]
        self.sort()
        self._loaded = True

    def load(self):
        pass


def cal(cls):
    eva = cls(FakeDataLoader)
    assert eva.data_loader.loaded
    results = eva.calculate_all()
    for i in results:
        if i.subset:
            assert sum([x.amount for x in i.subset]) == i.target.amount


def test_main():
    cal(BruteForceExecutor)
