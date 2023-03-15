[![workflow yamdb_final](https://github.com/FokinPV/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)](https://github.com/FokinPV/yamdb_final/actions/workflows/yamdb_workflow.yml)

# Дипломная работа - Foodgramm

## Стек: 
Django, django-filter djangorestframework-simplejwt, djangorestframework, PyJWT, pytest-django, pytest-pythonpath, asgiref, gunicorn, sqlparse

## Workflow

Для использования CI CD: 
в репозитории GitHub ActionsSettings/Secrets/Actions
прописать Secrets:


* DEBUG                          # режим откладки (False по умолчанию)
* ENGINE                         # ENGINE БД (django.db.backends.postgresql по умолчанию)
* DB_NAME                        # имя БД (postgres по умолчанию)
* POSTGRES_USER                  # логин для подключения к БД (postgres по умолчанию)
* POSTGRES_PASSWORD              # пароль для подключения к БД (установить свой)
* DB_HOST=db                     # название сервиса
* DB_PORT=5432                   # порт для подключения к БД


* DOCKER_USERNAME                # имя пользователя в DockerHub
* DOCKER_PASSWORD                # пароль пользователя в DockerHub
* HOST                           # ip_address сервера
* USER                           # имя пользователя
* SSH_KEY                        # приватный ssh-ключ
* PASSPHRASE                     # кодовая фраза (пароль) для ssh-ключа (если есть)

* TELEGRAM_TO                    # id аккаунта
* TELEGRAM_TOKEN                 # токен бота


## Подготовка удалённого сервера
* Войти на удалённый сервер, для этого необходимо знать адрес сервера, имя
пользователя и пароль. Адрес сервера указывается по IP-адресу или по доменному
имени:

ssh <username>@<ip_address>


* Остановить службу
nginx:

sudo systemctl stop nginx


* Установить Docker и Docker-compose:

sudo apt update
sudo apt upgrade -y
sudo apt install docker.io
sudo apt install docker-compose -y

* На сервере создать директорию
nginx:

mkdir  nginx/


* Скопировать файлы 
docker-compose.yaml
и
nginx/default.conf
из проекта (локально) на сервер в
home/<username>/docker-compose.yaml
и
home/<username>/nginx/default.conf
соответственно:
  * перейти в директорию с файлом
docker-compose.yaml
и выполните:
 
scp docker-compose.yaml <username>@<ip_address>:/home/<username>/docker-compose.yaml
  
  * перейти в директорию с файлом
default.conf
и выполните:
 

scp default.conf <username>@<ip_address>:/home/<username>/nginx/default.conf
  

## После успешного запуска контейнеров:
Создать миграции:

docker-compose exec backend python manage.py makemigrations

выполнить миграции:

docker-compose exec backend python manage.py migrate

Создать суперюзера:

docker-compose exec backend python manage.py createsuperuser

Собрать статику:

docker-compose exec web python manage.py collectstatic --no-input 





Автор: Фокин Павел


