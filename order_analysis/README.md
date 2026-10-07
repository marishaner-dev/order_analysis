# Анализ заказов интернет-магазина

Скрипт пакетно читает CSV с заказами, оставляет только доставленные (`status == Delivered`) и для каждого файла считает три метрики: общую выручку, средний чек и количество заказов. Результат всех файлов складывается в один отчёт. 


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


## Данные

В `data/` уже лежат файлы из датасета [Synthetic Order Records: 10K to 10M Records](https://www.kaggle.com/datasets/swainproject/synthetic-order-records-10k-to-10m-records) (CC BY 4.0, Swain / SwainLabs):

- `order_10000.csv`
- `order_100000.csv`
- `order_broken.csv` — учебный испорченный файл: в `total_amount` стоят нечисловые значения, чтобы проверить, что обработка не падает

Суммы в отчёте считаются как есть, без пересчёта валют: в задании нужно сложить `total_amount` доставленных заказов, а в файле одновременно встречаются USD, EUR и GBP.
