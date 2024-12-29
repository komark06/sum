import pytest

from src.executor import BruteForceExecutor
from test.utils import FakeDataLoader


@pytest.mark.parametrize("solvable", [(True), (False)])
def test_executor(solvable: FakeDataLoader):
    """Verify that BruteForceExecutor successfully solve problem."""
    data_loader = FakeDataLoader(solvable)
    data_loader.load()
    eva = BruteForceExecutor()
    results = eva.calculate_all(data_loader.targets, data_loader.numbers)
    for i in results:
        if i.subset:
            assert sum([x.amount for x in i.subset]) == i.target.amount
            assert solvable
        else:
            assert solvable is False
