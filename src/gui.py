"""This module is used to create GUI and use it."""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from src.data_loader import AbstractDataLoader, ExcelDataLoader
from src.executor import BruteForceExecutor, Result
from src.output import output_excel
from pathlib import Path
import multiprocessing


class GUI:

    def __init__(
        self,
        data_loader: AbstractDataLoader,
        executor: BruteForceExecutor,
    ):
        try:
            self.root = tk.Tk()
            self.data_loader = data_loader
            self.executor = executor
            self.label_var = tk.StringVar()
            root = self.root
            root.protocol("WM_DELETE_WINDOW", self.close)
            root.title("會計銷帳")
            root.minsize(400, 200)
            self.status_label = ttk.Label(
                self.root, textvariable=self.label_var
            )
            self.status_label.configure(
                font="-family {Microsoft JhengHei UI} -size 14"
            )
            style = ttk.Style()
            style.configure(
                "Custom.TButton", font=("Microsoft JhengHei UI", 12)
            )
            self.button = ttk.Button(
                self.root,
                style="Custom.TButton",
            )
            self.first_appearance()
            self.status_label.pack(pady=20)
            self.button.pack(pady=20)
        except Exception as e:
            messagebox.showerror("錯誤", f"GUI建立時發生錯誤: {str(e)}")
            raise e
        try:
            self.pool = multiprocessing.Pool()
        except Exception as e:
            messagebox.showerror("錯誤", f"無法建立 processes pool: {str(e)}")
            raise e

    def first_appearance(self):
        self.label_var.set("請選擇要讀取的檔案")
        self.button.configure(text="選擇檔案", command=self.run_action)

    def open_file(self):
        """Open file and load data from it."""
        try:
            file_path = filedialog.askopenfilename(
                title="讀取檔案", filetypes=[("*.xlsx *.xls", ".xlsx .xls")]
            )
            if not file_path:
                return
            self.data_loader.load(file_path, reload=True)
            filename = Path(file_path).name
            self.label_var.set(f"讀取檔案：{filename}")
        except Exception as e:
            messagebox.showerror("錯誤", f"檔案讀取時發生錯誤：{str(e)}")
            self.first_appearance()
            return
        return file_path

    def run_action(self):
        """Load data and use it to run executor."""
        if not self.open_file():
            return
        targets = self.data_loader.targets
        numbers = self.data_loader.numbers
        try:
            self.label_var.set("開始執行")
            self.button.configure(text="中止", command=self.close)
            self.async_result = self.pool.apply_async(
                self.executor.calculate_all,
                (targets, numbers),
                callback=self.save_file,
            )
        except Exception as e:
            messagebox.showerror("錯誤", f"啟動計算時發生錯誤：{str(e)}")
            raise e

    def save_file(self, results: list[Result]):
        try:
            filename = filedialog.asksaveasfilename(
                title="儲存檔案", filetypes=[("*.xlsx", ".xlsx")]
            )
            if not filename:
                filename = Path("export.xlsx").absolute()  # Default path
            output_excel(results, self.data_loader, filename)
            self.label_var.set(f"結果已經寫入 {filename}\n請選擇新檔案")
            self.button.configure(text="選擇檔案", command=self.run_action)
        except Exception as e:
            messagebox.showerror("錯誤", f"檔案寫入時發生錯誤：{str(e)}")
            raise e

    def close(self):
        print("執行清理動作...")
        self.pool.terminate()
        self.root.destroy()

    def mainloop(self):
        self.root.mainloop()


def run_gui():
    """Run the GUI.

    NOTE: This function must run straight after the
    if __name__ == '__main__' line of the main module.
    """
    multiprocessing.freeze_support()
    app = GUI(ExcelDataLoader(), BruteForceExecutor())
    app.mainloop()
