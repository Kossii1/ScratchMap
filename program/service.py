# КЛАСС ПО ОБЩИМ СЕРВИСНЫМ ОПЕРАЦИЯМ
from aifc import Error
import pymysql
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from program.structs import Country
from datetime import date
import os
from dotenv import load_dotenv
import requests

load_dotenv()  # Загружает переменные из .env файла

class Service:
    # инициализация хешера паролей Argon2 с заданными параметрами
    ph = PasswordHasher(time_cost=3, memory_cost=128 * 1024, parallelism=2)

    # подключение к базе данных MySQL
    @staticmethod
    def get_connection():
        conn = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "db_map")
        )
        # возвращаем объект соединения
        return conn

    # проверка на существование сессии
    @staticmethod
    def check_session(request):
        try:
            # проверяем, есть ли ключ 'UserStatus' в сессии
            if request.session['UserStatus'] is not None:
                # если статус равен 'User' или 'Admin' — сессия действительна
                if str(request.session['UserStatus']) == 'User' or str(request.session['UserStatus']) == 'Admin':

                    return True
                else:
                    # если значение не 'User' и не 'Admin' — недействительно
                    return False
            else:
                # если ключ отсутствует или None — недействительно
                return False
        except:
            # если возникло любое исключение (например, ключ не найден) — недействительно
            return False

    # хеширование пароля пользователя
    @staticmethod
    def hash_password(password: str) -> str:
        # используем заранее инициализированный PasswordHasher (Argon2) для создания безопасного хеша пароля
        return Service.ph.hash(password)

    # проверка пароля пользователя на соответствие хешу
    @staticmethod
    def verify_password(stored_hash: str, password: str) -> bool:
        try:
            # сравниваем введённый пароль с сохранённым хешем
            Service.ph.verify(stored_hash, password)
            return True
        except VerifyMismatchError:
            return False

    # получение id пользователя по логину в базе данных
    @staticmethod
    def get_id_user(login = ''):
        result = 0
        try:
            # подключение к базе данных
            conn = Service.get_connection()
            cursor = conn.cursor()

            # получение id по логину
            cursor.execute("SELECT id FROM users WHERE login = %s", (login,))

            # получаем первую запись, если пользователь найден
            row = cursor.fetchone()
            if row is not None:
                # сохраняем id пользователя
                result = row[0]

            # закрываем курсор и соединение
            cursor.close()
            conn.close()
        except Error as e:
            print(e)
        # возвращаем id пользователя (0, если не найден)
        return result

    # получение списка всех стран
    @staticmethod
    def get_countries():
        # список стран, который будет возвращён
        result = []
        try:
            # подключение к базе данных
            conn = Service.get_connection()
            cursor = conn.cursor()

            # Проверяем, есть ли данные в таблице
            cursor.execute('SELECT COUNT(*) FROM countries')
            count = cursor.fetchone()[0]

            if count == 0:
                # Если таблица пустая — загружаем через REST Countries
                url = "https://restcountries.com/v3.1/all?fields=name,cca2,translations"
                response = requests.get(url)
                if response.status_code == 200:
                    countries_data = response.json()
                    for country in countries_data:
                        name_ru = country.get('translations', {}).get('rus', {}).get('common') \
                                  or country['name']['common']
                        short_name = country.get('cca2', '')
                        if short_name:
                            cursor.execute(
                                'INSERT INTO countries (name, short_name) VALUES (%s, %s)',
                                (name_ru, short_name)
                            )
                    conn.commit()

            # выбираем id, имя и короткое имя всех стран, сортируем по имени
            cursor.execute('SELECT id,name,short_name FROM countries ORDER BY name')
            rows = cursor.fetchall()

            # создаём объекты Country и добавляем их в список
            for row in rows:
                country = Country(row[0], row[1], row[2])
                result.append(country)

            # закрываем курсор и соединение
            cursor.close()
            conn.close()
        except Error as e:
            print(e)

        # возвращаем список объектов стран
        return result

    # получение данных по стране
    @staticmethod
    def get_country(id_country):
        # создаём пустой объект Country для результата
        result = Country()
        try:
            # подключение к базе данных
            conn = Service.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id,name,short_name FROM countries WHERE id=%s', (id_country,))
            row = cursor.fetchone()

            # если страна найдена, заполняем поля объекта
            if row is not None:
                result.country_id = row[0]
                result.name = row[1]
                result.short_name = row[2]

            # закрываем курсор и соединение
            cursor.close()
            conn.close()
        except Error as e:
            print(e)

        # возвращаем объект Country
        return result

    # добавление цвета и впечатлений от страны, если их еще нет в бд
    @staticmethod
    def add_col_des(id_user = 0, id_country = 0):
        # по умолчанию id записи = 0 (не существует)
        result = 0
        try:
            # подключение к базе данных
            conn = Service.get_connection()
            cursor = conn.cursor()

            # проверяем, есть ли уже запись посещения пользователем этой страны
            query = 'SELECT id FROM colorcountries WHERE id_user=%s AND id_country=%s'
            args = (id_user, id_country)
            cursor.execute(query, args)
            row = cursor.fetchone()

            # если запись найдена, сохраняем её id
            if row is not None:
                result = row[0]

            # если записи нет — создаём новые записи в обеих таблицах
            if result == 0:
                # вставляем запись о цвете страны по умолчанию
                query = 'INSERT INTO colorcountries(id_user,id_country,color) VALUES(%s,%s,%s)'
                args = (id_user, id_country, '#9ed14a')
                cursor.execute(query, args)
                conn.commit()

                # вставляем запись о впечатлениях пользователя (пустое описание)
                query = 'INSERT INTO descriptioncountries(id_user,id_country,description) VALUES(%s,%s,%s)'
                args = (id_user, id_country, '')
                cursor.execute(query, args)
                conn.commit()

            # закрываем соединение
            cursor.close()
            conn.close()
        except Error as e:
            print(e)

        # возвращаем id записи (0, если запись не найдена и не вставлена)
        return result

    # форматирование объекта date в строку вида "DD.MM.YYYY"
    @staticmethod
    def get_text_date(d: date):
        result = ''
        # добавляем ведущий ноль к дню, если день меньше 10
        if d.day < 10: result = '0'
        # добавляем день
        result += str(d.day) + '.'

        # добавляем ведущий ноль к месяцу, если месяц меньше 10
        if d.month < 10: result += '0'
        # добавляем месяц
        result += str(d.month) + '.'

        # добавляем год
        result += str(d.year)

        # возвращаем строковое представление даты
        return result
