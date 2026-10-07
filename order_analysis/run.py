"""Запуск пакетного анализа заказов."""

import config
from src.analyzer import OrderAnalyzer


def main() -> None:
    analyzer = OrderAnalyzer(
        data_dir=config.DATA_DIR,
        reports_dir=config.REPORTS_DIR,
        logs_dir=config.LOGS_DIR,
        report_filename=config.REPORT_FILENAME,
        log_filename=config.LOG_FILENAME,
        status_column=config.STATUS_COLUMN,
        delivered_status=config.DELIVERED_STATUS,
        amount_column=config.AMOUNT_COLUMN,
        required_columns=config.REQUIRED_COLUMNS,
    )
    processed, failed = analyzer.process_all()
    print(f"Обработано файлов: {processed}")
    print(f"Файлов с ошибками: {failed}")
    print(f"Отчёт: {config.REPORTS_DIR / config.REPORT_FILENAME}")


if __name__ == "__main__":
    main()
