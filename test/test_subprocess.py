import multiprocessing
import queue
from unittest.mock import Mock

import pytest

from src.executor import BruteForceExecutor
from src.subprocess import SubprocessManager, _calculate
from test.utils import ExceptionExecutor, FakeDataLoader, InfiniteExecutor


@pytest.fixture
def manager_instance():
    manager = SubprocessManager()
    yield manager
    manager.terminate()


def test_calculate():
    """Test the _calculate function."""
    queue = multiprocessing.Queue()
    executor = BruteForceExecutor()
    data_loader = FakeDataLoader()
    _calculate(executor, queue, data_loader.targets, data_loader.numbers, -1.0)
    assert not queue.empty()


def test_start_calculation(manager_instance: SubprocessManager):
    """Test the start_calculation method of the SubprocessManager."""
    results = None

    def get_results(outcome):
        nonlocal results
        results = outcome

    data_loader = FakeDataLoader()
    manager_instance.start_calculation(
        BruteForceExecutor(),
        data_loader.targets,
        data_loader.numbers,
        get_results,
    )
    while manager_instance.is_running():
        pass
    assert results


def test_start_calculation_error(manager_instance: SubprocessManager):
    """Test error callback of start_calculation in SubprocessManager."""
    error_callback = Mock()
    data_loader = FakeDataLoader()
    manager_instance.start_calculation(
        ExceptionExecutor(),
        data_loader.targets,
        data_loader.numbers,
        error_callback=error_callback,
    )
    while manager_instance.is_running():
        pass
    error_callback.assert_called_once()


def test_is_running(manager_instance: SubprocessManager):
    """Test the is_running method of the SubprocessManager."""
    data_loader = FakeDataLoader()
    assert not manager_instance.is_running()
    manager_instance.start_calculation(
        InfiniteExecutor(),
        data_loader.targets,
        data_loader.numbers,
    )
    assert manager_instance.is_running()


def test_stop_calculation(manager_instance: SubprocessManager):
    """Test the stop_calculation method of the SubprocessManager."""
    data_loader = FakeDataLoader()
    manager_instance.start_calculation(
        InfiniteExecutor(),
        data_loader.targets,
        data_loader.numbers,
    )
    manager_instance.stop_calculation()
    assert not manager_instance.is_running()


def test_update_status(manager_instance: SubprocessManager):
    """Test the update_status method of the SubprocessManager."""
    manager_instance.queue = Mock()
    expected_progress = 0.5
    manager_instance.queue.get_nowait.return_value = expected_progress
    progress = manager_instance.update_status()
    assert progress == expected_progress


def test_update_status_empty(manager_instance: SubprocessManager):
    """Test update_status method of SubprocessManager.

    Test when the queue is empty.
    """
    manager_instance.queue = Mock()
    exception = queue.Empty
    manager_instance.queue.get_nowait.side_effect = exception
    progress = manager_instance.update_status()
    assert progress is None
