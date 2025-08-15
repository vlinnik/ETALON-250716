# Проект АСУ PYSCA-HMI 

Проект автоматизации линии приготовления бетона 

- Логика управления написана для контроллера KRAX PLC-932
- Визуализация написана на python3+PyQt5

# Запуск

## Имитация (без контроллера)

```
python3 -m gui --simulator
```

## Обычный запуск

Без использования ключа --device PLC предполагается на 192.168.2.10
```
python3 -m gui 
```

## Зависимости

AnyQt, PyQt5, pyplc, pysca, pygui


# Кастомные Widget на python

Home.ui использует Widgets, которые сделаны на python-е. Чтобы стали доступны в панели нужно

Из каталога проекта (где файлы *plugin.py)

```
PYQTDESIGNERPATH=. designer
```

в designer должен быть установлен libpyqt5/libpyqt5 