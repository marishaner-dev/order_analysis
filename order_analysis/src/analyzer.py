"""Пакетный анализ заказов интернет-магазина."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd


class DataFileError(Exception):
    """Файл с заказами нельзя использовать для расчёта метрик."""


class OrderAnalyzer:
    """Читает CSV с заказами, считает метрики доставленных и пишет общий отчёт.

    Повреждённый файл не останавливает пакет: ошибка уходит в лог, обработка
    продолжается со следующего файла.
    """

    def __init__(
        self,
        data_dir: Path,
        reports_dir: Path,
        logs_dir: Path,
        report_filename: str,
        log_filename: str,
        status_column: str,
        delivered_status: str,
        amount_column: str,
        required_columns: tuple[str, ...],
    ) -> None:
        self.data_dir = Path(data_dir)
        self.reports_dir = Path(reports_dir)
        self.logs_dir = Path(logs_dir)
        self.report_filename = report_filename
        self.log_filename = log_filename
        self.status_column = status_column
        self.delivered_status = delivered_status
        self.amount_column = amount_column
        self.required_columns = required_columns
        self._logger: logging.Logger | None = None

    def load_file(self, file_path: Path) -> pd.DataFrame:
        """Загружает один CSV и проверяет, что по нему можно считать метрики."""
        try:
            orders = pd.read_csv(file_path, encoding="utf-8")
        except pd.errors.EmptyDataError as exc:
            raise DataFileError("файл пуст или не содержит данных") from exc
        except pd.errors.ParserError as exc:
            raise DataFileError(f"неверный формат CSV: {exc}") from exc
        except UnicodeDecodeError as exc:
            raise DataFileError(f"не удалось декодировать файл: {exc}") from exc
        except OSError as exc:
            raise DataFileError(f"не удалось прочитать файл: {exc}") from exc

        missing = [
            column for column in self.required_columns if column not in orders.columns
        ]
        if missing:
            names = ", ".join(missing)
            raise DataFileError(f"неверный формат: нет колонок {names}")

        if orders.empty:
            raise DataFileError("файл пуст")

        numeric_amount = pd.to_numeric(orders[self.amount_column], errors="coerce")
        invalid_count = int(numeric_amount.isna().sum())
        if invalid_count:
            raise DataFileError(
                f"в колонке {self.amount_column} есть нечисловые или пустые "
                f"значения: {invalid_count}"
            )

        orders = orders.copy()
        orders[self.amount_column] = numeric_amount
        return orders

    def filter_delivered(self, orders: pd.DataFrame) -> pd.DataFrame:
        """Оставляет только заказы со статусом доставки из настроек."""
        status = orders[self.status_column].astype(str).str.strip()
        return orders.loc[status == self.delivered_status].copy()

    def calculate_metrics(self, orders: pd.DataFrame) -> dict[str, float | int]:
        """Считает выручку, средний чек и число заказов."""
        orders_count = int(len(orders))
        if orders_count == 0:
            return {
                "orders_count": 0,
                "total_revenue": 0.0,
                "average_check": 0.0,
            }

        total_revenue = round(float(orders[self.amount_column].sum()), 2)
        average_check = round(float(orders[self.amount_column].mean()), 2)
        return {
            "orders_count": orders_count,
            "total_revenue": total_revenue,
            "average_check": average_check,
        }

    def process_file(self, file_path: Path) -> dict[str, float | int | str] | None:
        """Считает метрики одного файла. При ошибке пишет лог и возвращает None."""
        try:
            orders = self.load_file(file_path)
            delivered = self.filter_delivered(orders)
            metrics = self.calculate_metrics(delivered)
        except DataFileError as exc:
            self._log_error(file_path, str(exc))
            return None
        except Exception as exc:
            self._log_error(file_path, f"не удалось обработать файл: {exc}")
            return None

        return {
            "file_name": file_path.name,
            "orders_count": metrics["orders_count"],
            "total_revenue": metrics["total_revenue"],
            "average_check": metrics["average_check"],
        }

    def process_all(self) -> tuple[int, int]:
        """Обрабатывает все CSV в папке данных и сохраняет общий отчёт.

        Возвращает число успешных файлов и число файлов с ошибками.
        """
        if not self.data_dir.is_dir():
            raise FileNotFoundError(f"папка с данными не найдена: {self.data_dir}")

        rows: list[dict[str, float | int | str]] = []
        failed = 0
        for file_path in sorted(self.data_dir.glob("*.csv")):
            metrics = self.process_file(file_path)
            if metrics is None:
                failed += 1
            else:
                rows.append(metrics)

        self._save_report(rows)
        return len(rows), failed

    def _save_report(self, rows: list[dict[str, float | int | str]]) -> None:
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        report = pd.DataFrame(
            rows,
            columns=["file_name", "orders_count", "total_revenue", "average_check"],
        )
        report_path = self.reports_dir / self.report_filename
        report.to_csv(report_path, index=False, float_format="%.2f")

    def _log_error(self, file_path: Path, message: str) -> None:
        logger = self._get_logger()
        logger.error("%s: %s", file_path.name, message)

    def _get_logger(self) -> logging.Logger:
        if self._logger is not None:
            return self._logger

        self.logs_dir.mkdir(parents=True, exist_ok=True)
        log_path = (self.logs_dir / self.log_filename).resolve()
        logger = logging.getLogger("order_analysis")
        logger.setLevel(logging.ERROR)
        logger.propagate = False

        already_attached = any(
            isinstance(handler, logging.FileHandler)
            and Path(handler.baseFilename).resolve() == log_path
            for handler in logger.handlers
        )
        if not already_attached:
            handler = logging.FileHandler(log_path, encoding="utf-8")
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            )
            logger.addHandler(handler)

        self._logger = logger
        return logger
