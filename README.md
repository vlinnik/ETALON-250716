# Проект АСУ etalon-250716 

Проект автоматизации  

- Логика управления написана для контроллера KRAX PLC-932
- Визуализация написана на python3+qtpy

# Запуск

Если запускаем из исходников, то

```
PYTHONPATH=src python3 -m gui
```

## Зависимости

PyQt, PyQt5/PyQt6, pysca, opentsdb-py, grafana-client и д.р.

# Установка

# Сборка 

# Кастомные Widget на python

Чтобы widgets из src/gui/data/widgets стали доступны в панели designer нужно

```
PYSCAWIDGETSPATH=src/gui/data/widgets designer
```

в designer должен быть установлен libpyqt5/libpyqt6 и pysca