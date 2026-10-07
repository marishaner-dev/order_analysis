# Анализ заказов интернет-магазина

Скрипт пакетно читает CSV с заказами, оставляет только доставленные (`status == Delivered`) и для каждого файла считает три метрики: общую выручку, средний чек и количество заказов. Результат всех файлов складывается в один отчёт. Если файл пустой, битый или в `total_amount` есть нечисловые значения, скрипт пропускает его, пишет причину в `logs/errors.log` и идёт дальше.

## Как запустить

Нужен Python 3.8 или новее.

```bash
pip install -r requirements.txt
python run.py
```

В консоли будет число успешно обработанных файлов и число файлов с ошибками. Отчёт появится в `reports/summary_report.csv`.

## Структура

```
data/                  # исходные CSV
reports/               # summary_report.csv
logs/                  # errors.log
src/analyzer.py        # класс OrderAnalyzer
config.py              # пути, имя отчёта, колонка и значение статуса
run.py                 # точка входа
requirements.txt
```

Настройки путей, имени отчёта, колонки статуса и значения `Delivered` лежат в `config.py`. Класс `OrderAnalyzer` сам находит все `*.csv` в `data/`, поэтому новый файл достаточно положить в эту папку и снова запустить `python run.py`.

## Данные

В `data/` уже лежат файлы из датасета [Synthetic Order Records: 10K to 10M Records](https://www.kaggle.com/datasets/swainproject/synthetic-order-records-10k-to-10m-records) (CC BY 4.0, Swain / SwainLabs):

- `order_10000.csv`
- `order_100000.csv`
- `order_broken.csv` — учебный испорченный файл: в `total_amount` стоят нечисловые значения, чтобы проверить, что обработка не падает

Суммы в отчёте считаются как есть, без пересчёта валют: в задании нужно сложить `total_amount` доставленных заказов, а в файле одновременно встречаются USD, EUR и GBP.
