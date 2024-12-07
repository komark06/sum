from datetime import date
from io import BytesIO
from itertools import zip_longest

import openpyxl

from src.data_loader import AbstractDataLoader, Summons
from src.executor import Result
from src.output import output_excel


class FakeDataLoader(AbstractDataLoader):
    """A fake data loader that simulates ExcelDataLoader.

    This loader is designed to mimic the functionality of ExcelDataLoader
    by generating a set of numbers and targets to simulate solving the
    subset sum problem.
    """

    def load(self):
        """Load simulated data.

        This method generates a set of numbers and targets. If the
        `solvable` flag is True, the target will be a subset sum
        achievable from the numbers. Otherwise, it will generate a
        target that is not achievable.
        """
        numbers = [i for i in range(10)]
        targets = [numbers[0], numbers[1] + numbers[2]]

        self.targets = [
            Summons("targets", date(2020, 1, 1), target) for target in targets
        ]
        self.numbers = [
            Summons("numbers", date(2020, 1, 1), number) for number in numbers
        ]
        self.sort()
        self._loaded = True


def test_output_excel():
    """Verify that output_excel successfully save output to file."""
    data_loader = FakeDataLoader()
    data_loader.load()
    results = [
        Result(data_loader.targets[0], [data_loader.numbers[0]]),
        Result(
            data_loader.targets[1],
            [data_loader.numbers[1], data_loader.numbers[2]],
        ),
    ]
    with BytesIO() as file:
        output_excel(results, data_loader, file)
        workbook = openpyxl.load_workbook(file)

        sheet = workbook[workbook.sheetnames[0]]
        for row, target, number in zip_longest(
            sheet.iter_rows(min_row=2, values_only=True),
            data_loader.targets,
            data_loader.numbers,
        ):
            if target:
                assert target == Summons(row[0], target.date, row[1])
            if number:
                assert number == Summons(row[3], number.date, row[4])
        sheet = workbook[workbook.sheetnames[1]]
        for idx, result in enumerate(results):
            # Dynamically calculate the starting column for this result
            start_column = idx * 5 + 1
            assert sheet.cell(2, start_column).value == result.target.account
            assert (
                sheet.cell(2, start_column + 1).value == result.target.amount
            )
            for i, number in enumerate(result.subset, start=2):
                assert (
                    sheet.cell(
                        i,
                        start_column + 2,
                    ).value
                    == number.account
                )
                assert (
                    sheet.cell(i, start_column + 3, number.amount).value
                    == number.amount
                )
