import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from src.data_loader import Summons
from src.executor import BruteForceExecutor, Result
from src.gui import GUI
from src.subprocess import SubprocessManager
from test.utils import (
    FakeDataLoader,
    FakeSubprocessManager,
    ImmediateSubprocessManager,
    InfiniteExecutor,
)


def _create_gui_instance(data_loader, executor, manager, interval=1.0):
    """Factory function to create a GUI instance and ensure cleanup."""
    gui = GUI(data_loader, executor, manager, interval)
    yield gui
    gui.cleanup()


@pytest.fixture
def gui_instance_infinite():
    """Create a GUI instance with infinite executor."""
    yield from _create_gui_instance(
        FakeDataLoader(), InfiniteExecutor(), SubprocessManager(), 0.0
    )


@pytest.fixture
def gui_instance_fake_manager():
    """Create a GUI instance with a fake subprocess manager.

    This fixture is useful when the subprocess manager is not needed,
    as it avoids initializing any real subprocess manager, which can
    speed up tests.
    """
    yield from _create_gui_instance(
        FakeDataLoader(), BruteForceExecutor(), FakeSubprocessManager()
    )


@pytest.fixture
def gui_instance_immediate():
    """Create a GUI instance that returns results immediately."""
    yield from _create_gui_instance(
        FakeDataLoader(), BruteForceExecutor(), ImmediateSubprocessManager()
    )


def test_gui_initialization(gui_instance_fake_manager: GUI):
    """Test GUI initialization."""
    assert gui_instance_fake_manager.root
    assert gui_instance_fake_manager.data_loader
    assert gui_instance_fake_manager.executor
    assert gui_instance_fake_manager.manager


def test_gui_initialization_failure():
    """Test GUI initialization failure.

    Ensure that the GUI shows an error message when it fails to
    initialize. Also, ensure that the cleanup method is called.
    """
    with patch(
        "src.gui.GUI._init_tk", side_effect=ValueError("Simulated GUI Error")
    ), patch("tkinter.messagebox.showerror") as mock_showerror, patch(
        "src.gui.GUI.cleanup"
    ) as mock_cleanup:
        with pytest.raises(ValueError, match="Simulated GUI Error"):
            GUI(
                FakeDataLoader(), BruteForceExecutor(), FakeSubprocessManager()
            )
        mock_cleanup.assert_called_once()
        mock_showerror.assert_called_once_with(
            "錯誤", f"初始化失敗: {"Simulated GUI Error"}"
        )


def test_set_initial_state(gui_instance_fake_manager: GUI):
    """Test the GUI state when it is initialized."""
    assert gui_instance_fake_manager.label_var.get() == "請選擇要讀取的檔案"
    assert gui_instance_fake_manager.button.cget("text") == "選擇檔案"


def test_set_running_state(gui_instance_infinite: GUI):
    """Test the GUI state when the calculation is running."""
    with patch("src.gui.GUI.open_file", return_value="test.xlsx"):
        gui_instance_infinite.run_action()
        assert gui_instance_infinite.label_var.get() == "開始執行"
        assert gui_instance_infinite.button.cget("text") == "中止"
    gui_instance_infinite.cleanup()


def test_handle_error(gui_instance_fake_manager: GUI):
    """Test the handle_error method of the GUI."""
    error_message = "Simulated Error"
    with patch("tkinter.messagebox.showerror") as mock_showerror, patch.object(
        gui_instance_fake_manager,
        "set_initial_state",
        wraps=gui_instance_fake_manager.set_initial_state,
    ) as mocked_set_initial_state:
        gui_instance_fake_manager.handle_error(error_message)
        mock_showerror.assert_called_once_with("錯誤", error_message)
        mocked_set_initial_state.assert_called_once()


@pytest.mark.parametrize(
    "filename",
    [
        "test.xlsx",
        None,
    ],
)
def test_open_file(filename: str | None, gui_instance_fake_manager: GUI):
    """Test the open_file method of the GUI."""
    with patch("tkinter.filedialog.askopenfilename", return_value=filename):
        file_path = gui_instance_fake_manager.open_file()
        assert file_path == filename
        if filename:
            assert (
                gui_instance_fake_manager.label_var.get()
                == f"讀取檔案：{filename}"
            )
        else:
            assert (
                gui_instance_fake_manager.label_var.get()
                == "請選擇要讀取的檔案"
            )


@pytest.mark.parametrize(
    "filename",
    [
        "test.xlsx",
        None,
    ],
)
def test_save_file(filename: str | None, gui_instance_fake_manager: GUI):
    """Test the save_file method of the GUI."""
    results = [
        Result(
            Summons("test", datetime.date(2020, 1, 1), 1),
            [Summons("test", datetime.date(2020, 1, 1), 1)],
        )
    ]
    with patch(
        "tkinter.filedialog.asksaveasfilename", return_value=filename
    ), patch("src.gui.output_excel") as mock_output_excel:
        gui_instance_fake_manager.save_file(results)
        if not filename:
            filename = Path("export.xlsx").absolute()
        mock_output_excel.assert_called_once_with(
            results, gui_instance_fake_manager.data_loader, filename
        )
        assert (
            f"結果已經寫入 {filename}"
            in gui_instance_fake_manager.label_var.get()
        )
        assert gui_instance_fake_manager.button.cget("text") == "選擇檔案"


def test_save_file_failure(gui_instance_fake_manager: GUI):
    """Test the save_file method of the GUI when it fails."""
    error_message = "Simulated Save File Error"
    with patch(
        "tkinter.filedialog.asksaveasfilename",
        side_effect=ValueError(error_message),
    ), patch("src.gui.GUI.handle_error") as mock_handle_error:
        gui_instance_fake_manager.save_file(None)
        mock_handle_error.assert_called_once_with(
            f"檔案寫入時發生錯誤：{error_message}"
        )


def test_run_action(gui_instance_immediate: GUI):
    """Test the run_action method of the GUI."""

    with patch(
        "src.gui.GUI.open_file", return_value="test.xlsx"
    ), patch.object(
        gui_instance_immediate, "subprocess_done"
    ) as mock_subprocess_done:
        gui_instance_immediate.run_action()
        mock_subprocess_done.assert_called_once()
        assert (
            gui_instance_immediate.manager.results
            == mock_subprocess_done.call_args[0][0]
        )


@pytest.mark.parametrize(
    "target,base_error_message",
    [
        (
            "src.gui.GUI.open_file",
            "檔案讀取時發生錯誤：",
        ),
        (
            "src.gui.GUI.set_running_state",
            "啟動計算時發生錯誤：",
        ),
    ],
)
def test_run_action_failure(
    target: str, base_error_message: str, gui_instance_fake_manager: GUI
):
    """Test the run_action method of the GUI when it fails."""

    error_message = "Simulated Error"
    with patch(
        target,
        side_effect=ValueError(error_message),
    ), patch(
        "tkinter.filedialog.askopenfilename", return_value="test.xlsx"
    ), patch("src.gui.GUI.handle_error") as mock_handle_error:
        gui_instance_fake_manager.run_action()
        mock_handle_error.assert_called_once_with(
            f"{base_error_message}{error_message}"
        )


def test_stop_action(gui_instance_infinite: GUI):
    """Test the stop action method of the GUI."""
    with patch(
        "src.gui.GUI.open_file", return_value="test.xlsx"
    ), patch.object(
        gui_instance_infinite,
        "set_initial_state",
        wraps=gui_instance_infinite.set_initial_state,
    ) as mocked_set_initial_state:
        gui_instance_infinite.run_action()
        assert gui_instance_infinite.manager.is_running()
        gui_instance_infinite.stop_action()
        assert not gui_instance_infinite.manager.is_running()
        mocked_set_initial_state.assert_called_once()


@pytest.mark.parametrize(
    "target,base_error_message",
    [
        (
            "test.utils.FakeSubprocessManager.stop_calculation",
            "無法建立 processes pool 或 queue：",
        ),
        ("src.gui.GUI.set_initial_state", "無法更新GUI："),
    ],
)
def test_stop_action_failure(
    target: str, base_error_message: str, gui_instance_fake_manager: GUI
):
    """Test the stop action method of the GUI when it fails."""
    error_message = "Simulated Error"
    with patch(
        target,
        side_effect=ValueError(error_message),
    ), patch("src.gui.GUI.handle_error") as mock_handle_error:
        with pytest.raises(ValueError, match=error_message):
            gui_instance_fake_manager.stop_action()
        mock_handle_error.assert_called_once_with(
            f"{base_error_message}{error_message}"
        )
