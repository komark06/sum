"""This module is used to create GUI and use it."""

import multiprocessing
import multiprocessing.pool
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from src.data_loader import AbstractDataLoader, ExcelDataLoader, Summons
from src.executor import BruteForceExecutor, Result
from src.output import output_excel
from src.subprocess import AbstractSubprocessManager, SubprocessManager


class GUI:

    def __init__(
        self,
        data_loader: AbstractDataLoader,
        executor: BruteForceExecutor,
        manager: AbstractSubprocessManager,
        interval: float = 0.0,
    ):
        self.root = None
        self.data_loader = data_loader
        self.executor = executor
        self.interval = interval
        try:
            self._init_tk()
            self.manager = manager
        except Exception as e:
            messagebox.showerror("錯誤", f"初始化失敗: {str(e)}")
            self.cleanup()
            raise e

    def _init_tk(self):
        """Initialize the tkinter GUI."""
        font = None
        root = tk.Tk()
        self.label_var = tk.StringVar()
        self.root = root
        root.protocol("WM_DELETE_WINDOW", self.cleanup)
        root.title("會計銷帳")
        root.minsize(400, 200)
        self.status_label = ttk.Label(self.root, textvariable=self.label_var)
        self.status_label.config(font=(font, 14))
        style = ttk.Style()
        style.configure("Custom.TButton", font=(font, 12))
        self.button = ttk.Button(
            self.root,
            style="Custom.TButton",
        )
        self.set_initial_state()
        self.status_label.pack(pady=20)
        self.button.pack(pady=20)

    def cleanup(self):
        """Cleanup resources.

        Ignore any exceptions that may occur because the GUI is being closed.
        """
        try:
            self.manager.terminate()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass

    def set_initial_state(self):
        """Set the initial screen."""
        self.label_var.set("請選擇要讀取的檔案")
        self.button.configure(text="選擇檔案", command=self.run_action)

    def set_running_state(self):
        """Set the screen and command when calculation is running."""
        self.label_var.set("開始執行")
        self.button.configure(text="中止", command=self.stop_action)

    def handle_error(self, error_message):
        """Show error message and set screen to initial state."""
        messagebox.showerror("錯誤", error_message)
        self.set_initial_state()

    def subprocess_done(self, results: list[Result]):
        """Save the results."""
        self.save_file(results)

    def subprocess_error(self, e: BaseException):
        """Handle error from subprocess."""
        self.handle_error(f"計算時發生錯誤：{str(e)}")

    def update_status(self):
        """Update the status of the calculation."""
        if progress := self.manager.update_status():
            print(f"進度: {progress*100:.2%}")
            self.label_var.set(f"進度: {progress*100:.2%}")
        if self.manager.is_running():
            self.root.after(3000, self.update_status)

    def open_file(self):
        """Load data from file."""
        file_path = filedialog.askopenfilename(
            title="讀取檔案", filetypes=[("*.xlsx *.xls", ".xlsx .xls")]
        )
        if not file_path:
            return
        self.data_loader.load(file_path, reload=True)
        filename = Path(file_path).name
        self.label_var.set(f"讀取檔案：{filename}")
        return file_path

    def save_file(self, results: list[Result]):
        try:
            filename = filedialog.asksaveasfilename(
                title="儲存檔案",
                defaultextension=".xlsx",
                filetypes=[("*.xlsx", ".xlsx")],
            )
            if not filename:
                filename = Path("export.xlsx").absolute()  # Default path
            output_excel(results, self.data_loader, filename)
            self.label_var.set(f"結果已經寫入 {filename}\n請選擇新檔案")
            self.button.configure(text="選擇檔案", command=self.run_action)
        except Exception as e:
            self.handle_error(f"檔案寫入時發生錯誤：{str(e)}")

    def run_action(self):
        """Load data and start calculation."""
        try:
            if not self.open_file():
                return
        except Exception as e:
            self.handle_error(f"檔案讀取時發生錯誤：{str(e)}")
            return
        targets = self.data_loader.targets
        numbers = self.data_loader.numbers
        try:
            self.manager.start_calculation(
                self.executor,
                targets,
                numbers,
                self.subprocess_done,
                self.subprocess_error,
                self.interval,
            )
            self.set_running_state()
            self.update_status()
        except Exception as e:
            self.handle_error(f"啟動計算時發生錯誤：{str(e)}")

    def stop_action(self):
        """Stop the calculation and set screen to initial state."""
        try:
            self.manager.stop_calculation()
        except Exception as e:
            self.handle_error(f"無法建立 processes pool 或 queue：{str(e)}")
            raise e
        try:
            self.set_initial_state()
        except Exception as e:
            self.handle_error(f"無法更新GUI：{str(e)}")
            raise e

    def mainloop(self):
        self.root.mainloop()


def run_gui():
    """Run the GUI.

    NOTE: This function must run straight after the
    if __name__ == '__main__' line of the main module.
    """
    multiprocessing.freeze_support()
    app = GUI(ExcelDataLoader(), BruteForceExecutor(), SubprocessManager())
    app.mainloop()
