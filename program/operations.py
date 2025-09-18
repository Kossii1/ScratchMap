# КЛАСС ПО ОПЕРАЦИЯМ ПОЛЬЗОВАТЕЛЯ
from aifc import Error
from program.service import Service
from program.structs import Country, MyCountry

class OperationsUser:
    # Определяющая функция для авторизации и регистрации
    def sign_in_reg(self, request, select=0, name='', login='', password=''):
        result = {'result': False}
        if select == 1: # Если select = 1 → авторизация
            if self.sign_in(request, login, password):
                result = {'result': True}   # Успешный вход
            else:
                result = {'result': False, 'message': 'Не правильно введен логин и/или пароль.'}
        if select == 2: # Если select = 2 → регистрация
            # Вызываем функцию регистрации
            result = self.reg(request, name, login, password)
        return result   # Возвращаем результат операции

    # Авторизация пользователя
    def sign_in(self, request, login = '', password = ''):
        result = False
        try:
            conn = Service.get_connection() # Получаем соединение с БД
            cursor = conn.cursor()
            cursor.execute("SELECT id,login,password FROM users WHERE login = %s", (login,))
            row = cursor.fetchone()
            # Если пользователь с таким логином существует
            if row is not None:
                # Проверяем пароль
                correct_password = Service.verify_password(row[2], password)
                # Если пароль верный
                if correct_password:
                    result = True
                    # Устанавливаем статус сессии
                    request.session['UserStatus'] = 'User'
                    # Сохраняем ID пользователя в сессии
                    request.session['IdUser'] = row[0]
            cursor.close()
            conn.close()
        except Error as e:
            print(e)
        # Возвращаем результат авторизации (True/False)
        return result

    # Регистрация нового пользователя
    def reg(self, request, name = '', login = '', password = ''):
        result = {'result': False, 'message': 'Ошибка.'}
        # Проверяем, существует ли уже пользователь с таким логином
        if Service.get_id_user(login) > 0:
            result = {'result': False, 'message': 'Пользователь с логином ' + login + ' уже существует в системе.'}
            return result
        try:
            conn = Service.get_connection()
            cursor = conn.cursor()
            # Параметризованный запрос для безопасности
            query = 'INSERT INTO users(name,login,password) VALUES(%s,%s,%s)'
            # Хешируем пароль перед сохранением
            args = (name, login, Service.hash_password(password))
            cursor.execute(query, args)
            conn.commit()
            conn.close()
            result = {'result': True}
            # Получаем ID нового пользователя
            last_row_id = Service.get_id_user(login)
            request.session['UserStatus'] = 'User'
            request.session['IdUser'] = last_row_id
        except Error as e:
            print(e)
        # Возвращаем результат регистрации
        return result

    # получение данных по профайлу пользователя
    def get_profile(self, id_user):
        result = {'result': False, 'message:': 'Ошибка.'}
        try:
            # подключение к БД
            conn = Service.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name, login, password FROM users WHERE id = %s", (id_user,))

            row = cursor.fetchone()

            # если запись найдена — формируем успешный результат
            if row is not None:
                result = {'result': True, 'name': row[0], 'login': row[1]}

            # закрытие ресурсов
            cursor.close()
            conn.close()
        except Error as e:
            print(e)
        return result

    # сохранение профайла
    def save_profile(self, id_user = 0, name = '', login = '', password = ''):
        result = {'result': False, 'message': 'Ошибка'}
        # проверка: если найден пользователь с таким же логином, но это не текущий id — запрещаем сохранение
        id_user_base = Service.get_id_user(login)
        if id_user_base > 0 and id_user_base != id_user:
            result = {'result': False, 'message': 'Такой логин уже присутствует в системе.'}
        else:
            try:
                # подключение к БД
                conn = Service.get_connection()
                cursor = conn.cursor()

                # если пароль передан — обновляем с паролем
                if password:
                    query = 'UPDATE users SET name = %s, login = %s, password = %s WHERE id = %s'
                    args = (name, login, Service.hash_password(password), id_user)
                # если пароль пустой — обновляем только имя и логин
                else:
                    query = 'UPDATE users SET name = %s, login = %s WHERE id = %s'
                    args = (name, login, id_user)
                # выполняем запрос обновления
                cursor.execute(query, args)
                conn.commit()

                # закрытие соединения
                conn.close()
                result = {'result': True}
            except Error as e:
                print(e)
        return result

    # сохранение цвета и впечатления от страны
    def save_col_des_country(self, id_user, id_country, color, description):
        result = {'result': False, 'message': 'Произошла ошибка.'}
        try:
            # подключение к БД
            conn = Service.get_connection()
            cursor = conn.cursor()

            # проверяем, есть ли уже запись для данного пользователя и страны
            query = 'SELECT 1 FROM colorcountries WHERE id_user=%s AND id_country=%s'
            cursor.execute(query, (id_user, id_country))
            exists = cursor.fetchone() is not None

            # если запись существует → обновляем цвет и описание
            if exists:
                # обновляем цвет
                query = 'UPDATE colorcountries SET color = %s WHERE id_user = %s AND id_country=%s'
                args = (color, id_user, id_country)
                cursor.execute(query, args)
                conn.commit()

                # обновляем описание
                query = 'UPDATE descriptioncountries SET description = %s WHERE id_user = %s AND id_country=%s'
                args = (description, id_user, id_country)
                cursor.execute(query, args)
                conn.commit()
            # если записи нет → создаём новую
            else:
                # вставляем цвет
                query = 'INSERT INTO colorcountries(id_user,id_country,color) VALUES(%s,%s,%s)'
                args = (id_user, id_country, color)
                cursor.execute(query, args)
                conn.commit()

                # вставляем описание
                query = 'INSERT INTO descriptioncountries(id_user,id_country,description) VALUES(%s,%s,%s)'
                args = (id_user, id_country, description)
                cursor.execute(query, args)
                conn.commit()
            conn.close()
            # успешный результат
            result = {'result': True}
        except Error as e:
            print(e)
        return result

    # получение списка посещенных стран пользователем
    def get_countries_user(self, id_user = 0):
        # список стран, которые вернём как результат
        result = []
        try:
            # подключаемся к базе
            conn = Service.get_connection()
            cursor = conn.cursor()
            # собираем список стран и цветов выделения
            cursor.execute('SELECT id_country, color FROM colorcountries WHERE id_user=%s', (id_user,))

            rows = cursor.fetchall()

            # создаём объекты стран и добавляем их в список
            for row in rows:
                # получаем данные о стране по её id
                country_data = Service.get_country(row[0])
                # создаём объект Country
                country = Country(country_data.country_id, country_data.name, country_data.short_name)
                # создаём объект MyCountry (объект класса с информацией о стране,
                # описание, цвет страны, список фоток)
                my_country = MyCountry(country, '', row[1], [])
                result.append(my_country)

            # Проходим по списку всех стран, которые посетил пользователь
            for i in result:
                query = 'SELECT description FROM descriptioncountries WHERE id_user=%s AND id_country=%s'
                args = (id_user, i.country.country_id)
                cursor.execute(query, args)
                row = cursor.fetchone()
                # добавляем описание для каждой страны (если есть)
                if row is not None:
                    i.description = row[0]

            # Проходим по списку всех стран, которые посетил пользователь
            for i in result:
                list_id_photos = []
                query = 'SELECT id FROM photos WHERE id_user=%s AND id_country=%s'
                args = (id_user, i.country.country_id)
                cursor.execute(query, args)
                rows = cursor.fetchall()
                # добавляем фотки для каждой страны
                for row in rows:
                    list_id_photos.append(row[0])
                i.listIdPhotos = list_id_photos[:]
            cursor.close()
            conn.close()
        except Error as e:
            print(e)
        return result

    # сохранение фото
    def save_photo(self, id_photo = 0, id_user = 0, id_country = 0, title = '', date = '', description = '', image_photo64 = ''):
        result = {'result': True, 'message': 'Ошибка.'}
        try:
            # подключение к базе данных
            conn = Service.get_connection()
            cursor = conn.cursor()

            # если id_photo = 0 → новая фотография, вставляем запись
            if id_photo == 0:
                query = 'INSERT INTO photos(id_user,id_country,title,date,description,image) VALUES(%s,%s,%s,%s,%s,%s)'
                args = (id_user, id_country, title, date, description, image_photo64)
                cursor.execute(query, args)
                conn.commit()
            # иначе → обновляем существующую фотографию
            else:
                query = 'UPDATE photos SET title = %s, date=%s, description=%s, image=%s WHERE id=%s AND id_user = %s AND id_country=%s'
                args = (title, date, description, image_photo64, id_photo, id_user, id_country)
                cursor.execute(query, args)
                conn.commit()
            # если всё прошло успешно, результат — True
            result = {'result': True}
        except Error as e:
            print(e)
        return result

    # загрузка фото пользователя по стране
    def load_photos_country(self, id_user = 0, id_country = 0):
        result = {'result': False, 'message': 'Ошибка.'}
        # список фотографий, который будем возвращать
        photos = []
        try:
            # подключение к базе данных
            conn = Service.get_connection()
            cursor = conn.cursor()

            # формируем запрос для выборки всех фото пользователя по указанной стране
            query = 'SELECT id,title,date,description,image FROM photos WHERE id_user=%s AND id_country=%s'
            args = (id_user, id_country)
            cursor.execute(query, args)
            rows = cursor.fetchall()

            # проходим по каждой строке и формируем словарь с данными фото
            for row in rows:
                country = {'id': row[0], 'title': row[1], 'date': Service.get_text_date(row[2]), 'description': row[3], 'image': row[4]}
                photos.append(country)
            cursor.close()
            conn.close()

            # если успешно — результат True и добавляем список фото
            result = {'result': True, 'photos': photos}
        except Error as e:
            print(e)
        return result

    # получение данных по фото
    def get_photo(self, id_user = 0, id_photo = 0):
        result = {'result': False, 'message': 'Ошибка.'}
        # словарь для хранения данных фото
        photo = {}
        try:
            # подключение к базе данных
            conn = Service.get_connection()
            cursor = conn.cursor()
            # формируем запрос для получения данных конкретного фото по id фото и id пользователя
            query = 'SELECT id,title,date,description,image FROM photos WHERE id=%s AND id_user=%s'
            args = (id_photo, id_user)
            cursor.execute(query, args)
            # получаем одну запись (если фото найдено)
            row = cursor.fetchone()

            # если фото найдено — формируем словарь с его данными
            if row is not None:
                photo = {'id': row[0], 'title': row[1], 'date': str(row[2]), 'description': row[3], 'image': row[4]}
            cursor.close()
            conn.close()

            # успешный результат, добавляем словарь с фото
            result = {'result': True, 'photo': photo}
        except Error as e:
            print(e)
        return result

    # удаление фото
    def delete_photo(self, id_user, id_photo):
        result = {'result': False}
        try:
            # подключение к базе данных
            conn = Service.get_connection()
            cursor = conn.cursor()

            # формируем запрос на удаление фото по id фото и id пользователя
            query = 'DELETE FROM photos WHERE id=%s AND id_user=%s'
            args = (id_photo, id_user)
            cursor.execute(query, args)
            conn.commit()

            # закрываем курсор и соединение
            cursor.close()
            conn.close()

            # успешное удаление
            result = {'result': True}
        except Error as e:
            print(e)
        return result
