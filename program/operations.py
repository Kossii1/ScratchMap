# КЛАСС ПО ОПЕРАЦИЯМ ПОЛЬЗОВАТЕЛЯ
from aifc import Error
from program.service import Service


class OperationsUser:
    def sign_in_reg(self, request, select=0, name='', login='', password=''):
        result = {'result': False}
        if select == 1:
            if self.sign_in(request, login, password):
                result = {'result': True}
            else:
                result = {'result': False, 'message': 'Не правильно введен логин и/или пароль.'}
        if select == 2:
            result = self.reg(request, name, login, password)
        return result

    # авторизация
    def sign_in(self, request, login = '', password = ''):
        result = False
        try:
            conn = Service.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id,login,password FROM users WHERE login = '" + login + "'")
            row = cursor.fetchone()
            if row is not None:
                correct_password = Service.verify_password(row[2], password)
                if correct_password:
                    result = True
                    request.session['UserStatus'] = 'User'
                    request.session['IdUser'] = row[0]
            cursor.close()
            conn.close()
        except Error as e:
            print(e)
        return result

    # регистрация
    def reg(self, request, name = '', login = '', password = ''):
        result = {'result': False, 'message': 'Ошибка.'}
        if Service.get_id_user(login) > 0:
            result = {'result': False, 'message': 'Пользователь с логином ' + login + ' уже существует в системе.'}
            return result
        try:
            conn = Service.get_connection()
            cursor = conn.cursor()
            query = 'INSERT INTO users(name,login,password) VALUES(%s,%s,%s)'
            args = (name, login, Service.hash_password(password))
            cursor.execute(query, args)
            conn.commit()
            conn.close()
            result = {'result': True}
            last_row_id = Service.get_id_user(login)
            request.session['UserStatus'] = 'User'
            request.session['IdUser'] = last_row_id
        except Error as e:
            print(e)
        return result

    # получение списка посещенных стран пользователем
    def get_countries_user(self, id_user = 0):
        result = []
        return result

    # получение данных по профайлу пользователя
    def get_profile(self, id_user):
        result = {'result': False, 'message:': 'Ошибка.'}
        try:
            conn = Service.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name,login,password FROM users WHERE id = " + str(id_user))
            row = cursor.fetchone()
            if row is not None:
                password = 'Пароль'
                result = {'result': True, 'name': row[0], 'login': row[1], 'password': password}
            cursor.close()
            conn.close()
        except Error as e:
            print(e)
        return result
