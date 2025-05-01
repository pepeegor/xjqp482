# Развёртывание Django-приложения на Ubuntu 20.04+ (Nginx + Gunicorn)

## 1. Предварительные требования

Убедитесь, что на сервере установлены:

- Python 3.11 (или 3.12) с модулями venv и distutils
- pip (для Python 3.x)
- PostgreSQL
- Nginx
- Git

```
sudo apt update
sudo apt install -y git python3.11 python3.11-venv python3.11-distutils postgresql postgresql-contrib nginx
```

> При необходимости используйте PPA deadsnakes или сборку из исходников для Python 3.11/3.12.

## 2. Настройка PostgreSQL

1. Переключитесь на пользователя postgres:
```
sudo -u postgres psql
```
2. Создайте базу и роль (замените имя пользователя и пароль):
   ```
   CREATE DATABASE geoapp;
   CREATE USER geoappuser WITH PASSWORD 'StrongPassword!';
   GRANT ALL PRIVILEGES ON DATABASE geoapp TO geoappuser;
   \q
   ```

## 3. Клонирование проекта и виртуальное окружение

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/pepeegor/xjqp482.git geoapp
   cd geoapp
   ```
2. Создайте и активируйте venv:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```

## 4. Конфигурирование окружения

1. Скопируйте пример `.env-example` в `.env`:
   ```
   cp .env-example .env
   ```
2. В файле `.env` заполните:
   ```
   SECRET_KEY="<your-secret-key>"
   DEBUG=False
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=postgres://geoappuser:StrongPassword!@localhost:5432/geoapp
   ```

## 5. Миграции и статика

1. Примените миграции:
   ```
   python manage.py migrate
   ```
2. Соберите статические файлы:
   ```
   python manage.py collectstatic --noinput
   ```

## 6. Настройка Gunicorn сервиса

1. Скопируйте файл gunicorn.service в `/etc/systemd/system/gunicorn.service` и поменяйте следующие данные:

   ```
   [Unit]
   Description=Gunicorn Django Service
   After=network.target

   [Service]
   User=osboxes           # замените на вашего пользователя
   Group=www-data
   WorkingDirectory=/home/osboxes/geoapp
   Environment="PATH=/home/osboxes/geoapp/venv/bin"
   Environment=DJANGO_SETTINGS_MODULE=webapp.settings
   ExecStart=/home/osboxes/geoapp/venv/bin/gunicorn \
     --chdir /home/osboxes/geoapp \
     webapp.wsgi:application \
     --bind 127.0.0.1:8000 \
     --workers 3

   [Install]
   WantedBy=multi-user.target
   ```

2. Примените и запустите сервис:
   ```
   sudo systemctl daemon-reload
   sudo systemctl start gunicorn
   sudo systemctl enable gunicorn
   ```

## 7. Настройка Nginx

1. Скопируйте конфигурацию nginx-conf в `/etc/nginx/sites-available/geoapp` и подставьте свои данные:

   ```
   server {
       listen 80;
       server_name localhost;  # или ваш домен/IP

       location /static/ {
           alias /home/osboxes/geoapp/staticfiles/;
           expires max;
           add_header Cache-Control public;
       }

       location / {
           include proxy_params;
           proxy_pass http://127.0.0.1:8000;
       }
   }
   ```

2. Активируйте сайт и перезапустите Nginx, а также настройте доступ к статике:
   ```
   sudo ln -s /etc/nginx/sites-available/geoapp /etc/nginx/sites-enabled/
   sudo rm /etc/nginx/sites-enabled/default
   sudo nginx -t
   sudo chown -R <YOUR_USER>:www-data /home/<YOUR_USER>/geoapp/staticfiles
   sudo chmod -R 755 /home/<YOUR_USER>/geoapp/staticfiles
   sudo systemctl restart nginx
   sudo systemctl enable nginx
   ```

## 8. Доступ к приложению

- **На сервере:** откройте http://localhost/ или http://127.0.0.1/
- **Удалённо:** укажите IP сервера или домен в `server_name` и в браузере перейдите по нему.

Приложение готово к использованию. Все сервисы запускаются автоматически при перезагрузке системы.
