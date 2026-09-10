# zion_rates.exe

Утилита для получения курсов USD (CCL) и кросс-курсов к латиноамериканским валютам
через публичный API [zion.ar](https://zion.ar/api/v1/openapi).

## Что считает

- `USD/ARS` — курс доллара CCL (Contado con Liquidación) напрямую из API.
- `USD/BRL`, `USD/BOB`, `USD/COP`, `USD/PYG`, `USD/PEN` — синтетический
  (implied) CCL-кросс-курс, посчитанный через ARS как мост:

  ```
  USD/XXX = USDCCL(ARS за USD) / XXX(ARS за 1 XXX)
  ```

  Это не отдельно торгуемая рыночная котировка, а расчётный кросс-курс.

## Установка

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

## Запуск

```powershell
.\.venv\Scripts\python run.py --pretty
.\.venv\Scripts\python run.py -o rates.json
```

Флаги:
- `-o, --output` — путь к файлу для записи JSON (по умолчанию — stdout).
- `--pretty` — форматированный вывод JSON.

## Сборка exe

```powershell
.\.venv\Scripts\pip install -r requirements-dev.txt
.\.venv\Scripts\pyinstaller --onefile --name zion_rates --console --icon assets\icon.ico run.py
```

Готовый файл: `dist\zion_rates.exe`.

## Пример вывода

```json
{
  "source": "zion.ar",
  "base": "USD (CCL)",
  "updatedAt": 1789025100000,
  "updatedAtIso": "2026-09-10T07:25:00+00:00",
  "rates": [
    { "pair": "USD/ARS", "rate": 1591.5 },
    { "pair": "USD/BRL", "rate": 5.365043 },
    { "pair": "USD/BOB", "rate": 13.291417 },
    { "pair": "USD/COP", "rate": 3263.223076 },
    { "pair": "USD/PYG", "rate": 6206.686764 },
    { "pair": "USD/PEN", "rate": 3.530322 }
  ]
}
```
