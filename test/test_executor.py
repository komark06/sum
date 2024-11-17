import datetime
from src.data_loader import AbstractDataLoader, Summons
from src.executor import BruteForceExecutor


class FakeDataLoader(AbstractDataLoader):
    """A Fake Data Loader that simulate ExcelDataLoader."""

    def load(self):
        """Simulate the load method of ExcelDataLoader."""
        numbers = [i for i in range(23)]
        targets = [sum(numbers) + 1, numbers[-1]]

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


def test_executor():
    """Verify that BruteForceExecutor successfully solve problem."""
    data_loader = FakeDataLoader()
    data_loader.load()
    eva = BruteForceExecutor()
    results = eva.calculate_all(data_loader.targets, data_loader.numbers)
    for i in results:
        if i.subset:
            assert sum([x.amount for x in i.subset]) == i.target.amount