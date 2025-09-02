# КЛАСС ПО ОБЩИМ СЕРВИСНЫМ ОПЕРАЦИЯМ
from aifc import Error
import pymysql
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from program.structs import Country

class Service:
    ph = PasswordHasher(time_cost=3, memory_cost=128 * 1024, parallelism=2)

    # подключение к базе данных MySQL
    @staticmethod
    def get_connection():
        conn = pymysql.connect(host='localhost', port=3306, user='root', password='db_map1707',
                               database='db_map')
        return conn

    # проверка на существование сессии
    @staticmethod
    def check_session(request):
        try:
            if request.session['UserStatus'] is not None:
                if str(request.session['UserStatus']) == 'User' or str(request.session['UserStatus']) == 'Admin':
                    return True
                else:
                    return False
            else:
                return False
        except:
            return False

    @staticmethod
    def hash_password(password: str) -> str:
        return Service.ph.hash(password)

    @staticmethod
    def verify_password(stored_hash: str, password: str) -> bool:
        try:
            Service.ph.verify(stored_hash, password)
            return True
        except VerifyMismatchError:
            return False

    # получение id пользователя по логину в базе данных
    @staticmethod
    def get_id_user(login = ''):
        result = 0
        try:
            conn = Service.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE login = '" + login + "'")
            row = cursor.fetchone()
            if row is not None:
                result = row[0]
            cursor.close()
            conn.close()
        except Error as e:
            print(e)
        return result

    # получение списка всех стран
    @staticmethod
    def get_countries():
        result = []
        try:
            conn = Service.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id,name,short_name FROM countries ORDER BY name')
            rows = cursor.fetchall()
            for row in rows:
                country = Country(row[0], row[1], row[2])
                result.append(country)
            cursor.close()
            conn.close()
        except Error as e:
            print(e)
        return result