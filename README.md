### Интернет-магазин по доставке конфет "Сласти от всех напастей".


### Зависимости
Для работы приложения необходима версия языка Python 3.6 и выше

Зависимости для проекта описаны в файле requirements.txt

Используемые библиотеки:
- ```asgiref``` используется для обеспечения стандартного интерфейса между 
асинхронными веб-серверами, платформами и приложениями Python.
- ```Django``` фреймворк используется для построения веб-сервиса.
- ```djangorestframework``` фреймворк используется для создания API.
- ```psycopg2``` используется для связи веб-сервиса с СУБД Postgres.
- ```pycodestyle``` используется для проверки кода Python на соответствие 
стилевым соглашениям в PEP 8.
- ```pytz``` используется для определения мировых часовых поясов для Python.
- ```sqlparse``` используется для поддержки синтаксического анализа, 
разделения и форматирования операторов SQL.


### Установка
1)Для начала обновить локальную базу пакетов
```
sudo apt update
sudo apt upgrade
```
2)Установить необходимый набора пакетов
```
sudo apt install python3 python3-pip python3-venv git libpq-dev postgresql postgresql-server-dev-all nginx curl
```
3)Склонировать репозиторий с приложением в домашнюю директорию
```
git clone https://github.com/Borutia/Candy_delivery_app.git
```
4)Перейти в директорию с проектом 
```
cd Candy_delivery_app
```
5)Создать базу данных для приложения и его тестирования 
```
sudo su -c "sh create_db.sh" postgres
```
6)Создать виртуальное окружение
```
python3 -m venv venv
```
7)Активировать виртуальное окружение
```
source ./venv/bin/activate
```
8)Установить зависимости для приложения
```
pip install -r requirements.txt
```
9)Применить миграции к базе данных PostgreSQL
```
python3 manage.py migrate
```
10)Добавить ip виртуальной машины в settings в ALLOWED_HOSTS 
```
sudo vi /home/entrant/Candy_delivery_app/Candy_delivery_app/settings.py
```
11)Убедиться, что тесты приложения завершаются успешно
```
python3 manage.py test
```


### Развёртывание сайта и автоматический запуск RESP API
1)Проверить, что текущая директория с проектом Candy_delivery_app 
и активировано виртуальное окружение venv

2)Установить Gunicorn
```
pip install gunicorn
```
3)Создать и добавить информацию в файл сокета systemd для Gunicorn ```sudo vi /etc/systemd/system/gunicorn.socket```
```
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=0.0.0.0:8080

[Install]
WantedBy=sockets.target
```
4)Создать и добавить информацию в служебный файл systemd для Gunicorn ```sudo vi /etc/systemd/system/gunicorn.service```
```
sudo vi /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=entrant
Group=www-data
WorkingDirectory=/home/entrant/Candy_delivery_app
ExecStart=/home/entrant/Candy_delivery_app/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind 0.0.0.0:8080 \
          Candy_delivery_app.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```
5)Включить сервис и добавить автоматический запуск RESP API
```
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
```
6)Создать и добавить информацию в файл настройки Nginx ```sudo vi /etc/nginx/sites-available/Candy_delivery_app```

server_name - ip адрес машины
```
server {
    listen 80;
    server_name 178.154.197.21;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/entrant/Candy_delivery_app;
    }

    location / {
        include proxy_params;
        proxy_pass http://0.0.0.0:8080;
    }
}
```
7)Активировать файл, привязав его к каталогу sites-enabled
```
sudo ln -s /etc/nginx/sites-available/Candy_delivery_app /etc/nginx/sites-enabled
```
8)Перезапустить Nginx
```
sudo systemctl restart nginx
```


### Запуск тестов
Команда для запуска тестов
```
python3 manage.py test
```


### Запуск проверки кода по PEP 8
Команда для запуска проверки кода Python PEP 8
```
pycodestyle . --exclude=venv
```
