"""XML data loader."""

import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass

import openpyxl


@dataclass
class Summons:
    summons_account: str
    date: datetime.date
    amount: int


class AbstractDataLoader(ABC):
    """
    An abstract data loader.

    Attributes:
        targets (List[Summons]): The list of targets that we want to
            solve as subset sum target.
        numbers (List[Summons]): The subset that we search for the sum
            of its subset is equal to target.
    """

    targets: list[Summons]
    numbers: list[Summons]
    _loaded: bool

    def __init__(self):
        self._loaded = False

    @property
    def loaded(self):
        """
        Check data is loaded or not.

        If data is loaded, return True. Else, return false.
        """
        return self._loaded

    @abstractmethod
    def load(self):
        """Load data."""
        pass

    def sort(self):
        """Sort numbers and targets"""
        if self.loaded:
            self.numbers.sort(key=lambda x: (x.date, x.amount))
            self.targets.sort(key=lambda x: (x.date, x.amount))


class ExcelDataLoader(AbstractDataLoader):
    """A Data Loader load data from Excel."""

    def __init__(self):
        super().__init__()

    def load(self, filename="normal.xlsx", reload=False):
        if self.loaded and not reload:
            return
        workbook = openpyxl.load_workbook(filename)
        sheet = workbook.active
        start_header = "VOUCHER#"
        for row in sheet.iter_rows():
            if row[0].value == start_header:
                headers = [col.value for col in row]
                start_row = row[0].row + 1
                break
        else:
            raise ValueError("Header NOT FOUND!!")
        self.targets = []
        self.numbers = []
        for row in sheet.iter_rows(min_row=start_row, values_only=True):
            data = {key: value for key, value in zip(headers, row)}
            if data[start_header]:
                summons_account = data[start_header]
                amount = data["VOUCHER_AMT"]
                year = int(summons_account[:4])
                month = int(summons_account[4:6])
                day = int(summons_account[6:8])
                date = datetime.date(year, month, day)
                summons = Summons(summons_account, date, abs(amount))
                flag = data["D/C"]
                if flag == "D":
                    self.targets.append(summons)
                else:
                    self.numbers.append(summons)
        self._loaded = True
        self.sort()
