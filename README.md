# `Foodgram` - сайт 'Продуктовый помощник'

#### О проекте:
 Онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
 
#### Технологии:
- Python
- Django
- Django REST Framework
- PostgreSQL
- Nginx
- Gunicorn
- Docker

#### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

`git@github.com:ShineXo1/foodgram-project-react.git`

`cd foodgram-project-react`

Установить Docker и Docker Compose (нативная ОС для Docker — Linux, поэтому запуск Docker-контейнеров должен происходить внутри виртуальной машины с ОС Linux):

`sudo apt install docker-ce docker-compose -y`

Для работы с базой данных создать файл .env c переменными окружения. В директории backend/ проекта расположен файл .env.example, в котором описаны примеры переменных и их значений.

Запуск контейнера:

`docker-compose up -d`

Заполнение базы данными:

`sudo docker-compose exec backend python manage.py collectstatic --no-input`

`sudo docker-compose exec backend python manage.py makemigrations --noinput`

`sudo docker-compose exec backend python manage.py migrate --noinput`

`sudo docker-compose exec backend python manage.py createsuperuser`

`sudo docker-compose exec backend python manage.py loademodels`


Докуметация API:

`http://158.160.76.4/api/docs/redoc.html`

Проект:

`http://158.160.76.4`

`http://yapifoodgram.hopto.org`

Суперпользователь:

`Адрес электронной почты: grizle@bkb.ru`

`Пароль: Nhbnhjqrb333`
