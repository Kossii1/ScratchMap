# Map Project

Django-проект с интерактивной картой и подключением к MySQL.

## Требования

- Python 3.12.3
- Django 5.2.4
- MySQL
- Все зависимости указаны в `requirements.txt`

---

## Установка и запуск

1. **Склонируйте репозиторий:**  
git clone <URL_репозитория>  
cd map

2. **Создайте виртуальное окружение**

    (Linux/macOS):  
  python -m venv venv  
  source venv/bin/activate

      (Windows):
  python -m venv venv  
  venv\Scripts\activate

3. **Установите зависимости:**  
pip install -r requirements.txt

4. **Создайте пустую базу данных в MySQL** (например, через MySQL Workbench).

5. **Создайте файл `.env`** в корне проекта (рядом с `manage.py`) со следующим содержимым:  
```
DB_NAME=имя созданной БД
DB_USER=имя пользователя созданной БД
DB_PASSWORD=пароль созданной БД
DB_HOST=хост созданной БД
DB_PORT=порт созданной БД
```

6. **Примените миграции:**  
python manage.py makemigrations  
python manage.py migrate

7. **Запустите проект:**  
python manage.py runserver  

Сервер по умолчанию будет доступен по адресу: http://127.0.0.1:8000
