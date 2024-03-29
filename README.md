# Проект блога YATUBE

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)


## Описание проекта
Социальная сеть - блог.
Сайт создан, что бы любой желающий мог вести свой блог. Для этого нужно зарегистрироваться, авторизоваться и можно оставлять текстовые посты, добавлять к постам изображение (опционально). Пост может принадлежать какой-то группе или быть независимым. Посты публикуются на главно странице в порядке их добавления. Главная страница разбита на страницы по 10 постов. Посты можно фильтровать по автору или по группе. Авторизованный пользователь может оставлять комментарии под постами, подписываться на авторов, фильтровать посты по подпискам. Пользователь при необходимости может сменить пароль.

## Инструменты
- Django
- django.contrib.auth
- Bootstrap

## Инструкция по запуску локально

1. Клонировать репозиторий
2. Создать и активировать виртуальное окружение
```
python3 -m venv venv
```
3. Установить зависимости из файла ```requirements.txt```
```
pip install -r requirements.txt
```
4. Перейти в директорию ```/yatube``` и выполнить миграции
```
python3 manage.py migrate
```
5. Создать суперпользователя (при необходимости)
```
python3 manage.py createsuperuser
```
6. Запуск юнит-тестов командой (при необходимости)
```
python3 manage.py test
```
7. Запустить сервер командой
```
python3 manage.py runserver
```

* Примечания:
* Для запуска в режиме разработки в файле settings.py установить флаг ```DEBUG=True```, в противном случае не подгрузится статика.

Блог будет доступен по адресу:
http://127.0.0.1:8000/

Админ панель:
http://127.0.0.1:8000/admin


## Demo

Демонстрация блога запущена на сервисе PythonAnyWhere по адресу:
https://knightsd.pythonanywhere.com/

Для доступа к демо зарегистрируйте свою учетную запись или воспользуйтесь готовой:
Пользователь: vasya
Пароль: 7HGbdS54
