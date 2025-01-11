from unittest.mock import MagicMock

import pytest

from src.executor import BruteForceExecutor
from test.utils import FakeDataLoader


@pytest.mark.parametrize("solvable", [(True), (False)])
def test_executor(solvable: FakeDataLoader):
    """Verify that BruteForceExecutor successfully solve problem.

    Make sure that callback is called at least once.
    """
    mock_callback = MagicMock()

    data_loader = FakeDataLoader(solvable)
    eva = BruteForceExecutor()
    results = eva.calculate_all(
        data_loader.targets, data_loader.numbers, mock_callback
    )
    for i in results:
        if solvable:
            assert sum([x.amount for x in i.subset]) == i.target.amount
    mock_callback.assert_called()
    args, _ = mock_callback.call_args
    assert isinstance(args[0], float), f"Expected float, got {type(args[0])}"
