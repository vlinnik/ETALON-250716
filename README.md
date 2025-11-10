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

# TODO

В процессе подготовки к отгрузке, при проверке работы через pysca --settings settings.yaml выявлено

- неочевидно как сделать окна по шаблонам (Siever/GearROT) и чтобы можно было их использовать из Событий
- что надо добавлять MODULE='gui' и потом gui.Siever.show()
- что можно переопределить on_load/on_start в модуле загружаемом из settings.yaml:main->modules
- нет общего пространства чтобы достать Home/Dashboard, которые созданы через settings.yaml:navbar->pages