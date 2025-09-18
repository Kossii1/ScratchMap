from django.shortcuts import render
from program.operations import OperationsUser
from program.service import Service
import jsonpickle
import json
from django.http import HttpResponse

user_ops = OperationsUser() # указатель на класс операций пользователя


# рендерим стартовую страницу
def welcome_page(request):
    return render(request, 'welcome_page.html')

# авторизация или регистрация пользователя
def sign_in_reg(request):
    try:
        # получаем из формы, что выбрал пользователь: вход (1) или регистрация (2)
        # если поле отсутствует или не число, default = 0
        select = int(request.POST.get('select', 0))
    except (TypeError, ValueError):
        select = 0
    # получаем значения из формы, убираем лишние пробелы
    name = (request.POST.get('name') or '').strip()
    login = (request.POST.get('login') or '').strip()
    password = request.POST.get('password') or ''

    # вызываем метод класса OperationsUser для обработки авторизации/регистрации
    result = user_ops.sign_in_reg(request, select, name, login, password)

    # если авторизация или регистрация успешны, переходим на карту
    if result.get('result'):
        return show_map(request)
    else:
        # иначе показываем информацию об ошибке
        return show_info(request, result.get('message'))

# переход на карту
def show_map(request):
    # проверяем, авторизован ли пользователь (валидная сессия)
    if Service.check_session(request):
        # проверяем, что пользователь действительно имеет статус 'User'
        if str(request.session['UserStatus']) == 'User':
            id_user = request.session['IdUser'] # получаем id пользователя из сессии

            # получаем список стран, которые посетил пользователь
            list_my_countries = user_ops.get_countries_user(id_user)

            # получаем полный список стран
            list_countries = Service.get_countries()

            # кодируем объекты в JSON-строки для передачи в JS на странице
            data = {'ListMyCountries': jsonpickle.encode(list_my_countries, unpicklable=False),
                    'ListCountries': jsonpickle.encode(list_countries, unpicklable=False)}

            # рендерим страницу карты с переданными данными
            return render(request, 'map.html', context=data)

# переход на информационную страницу
def show_info(request, message):
    # передаем сообщение в шаблон info.html
    data = {'info': message}
    return render(request, 'info.html', context=data)

# получение данных по профайлу
def get_profile(request):
    # проверяем, что запрос GET
    if request.method == "GET":
        # проверка сессии (пользователь авторизован)
        if Service.check_session(request):
            # проверка, что пользователь имеет статус 'User'
            if str(request.session['UserStatus']) == 'User':
                id_user = request.session['IdUser'] # получаем id пользователя из сессии
                # получаем профиль пользователя через класс операций
                result = user_ops.get_profile(id_user)
            else:
                result = {'result': False, 'message:': 'Ошибка.'}
        else:
            result = {'result': False, 'message:': 'Ошибка.'}
    else:
        result = {'result': False, 'message:': 'Ошибка.'}

    # возвращаем результат в виде JSON
    return HttpResponse(json.dumps(result))

# сохранение профиля
def save_profile(request):
    # метод POST (лучше для передачи личных данных)
    if request.method == "POST":
        if Service.check_session(request):
            if str(request.session['UserStatus']) == 'User':
                id_user = request.session['IdUser']
                # извлекаем данные из POST-запроса
                name = str(request.POST.get('name'))
                login = str(request.POST.get('login'))
                password = str(request.POST.get('password'))
                # сохраняем профиль через класс операций
                result = user_ops.save_profile(id_user, name, login, password)
            else:
                result = {'result': False, 'message:': 'Ошибка.'}
        else:
            result = {'result': False, 'message:': 'Ошибка.'}
    else:
        result = {'result': False, 'message:': 'Ошибка.'}
    return HttpResponse(json.dumps(result))

# выход из аккаунта
def exit_profile(request):
    if request.method == "GET":
        if Service.check_session(request):
            if str(request.session['UserStatus']) == 'User':
                # сброс данных сессии при выходе
                request.session['UserStatus'] = ''
                request.session['IdUser'] = 0
                result = {'result': True}   # успешный выход
            else:
                result = {'result': False, 'message:': 'Ошибка.'}
        else:
            result = {'result': False, 'message:': 'Ошибка.'}
    else:
        result = {'result': False, 'message:': 'Ошибка.'}
    return HttpResponse(json.dumps(result))

# сохранение цвета и впечатления от страны
def save_col_des_country(request):
    # проверяем, что запрос POST (данные отправляются безопасно)
    if request.method == "POST":
        # проверка действительности сессии
        if Service.check_session(request):
            # проверка, что пользователь авторизован и имеет статус 'User'
            if str(request.session['UserStatus']) == 'User':
                id_user = request.session['IdUser']
                # получаем данные из POST-запроса
                id_country = int(str(request.POST.get('idCountry')))
                color = str(request.POST.get('color'))
                description = str(request.POST.get('description'))
                # сохраняем данные через класс операций пользователя
                result = user_ops.save_col_des_country(id_user, id_country, color, description)
            else:
                result={'result': False, 'message': 'Неавторизованный вход.'}
        else:
            result={'result': False, 'message': 'Закончилось время сессии.'}
    else:
        result = {'result': False, 'message': 'Не правильный запрос.'}

    # возвращаем результат операции в виде JSON
    return HttpResponse(json.dumps(result))

# получение списка стран, посещенных пользователем
def get_user_countries(request):
    if request.method == "GET":
        if Service.check_session(request):
            if str(request.session['UserStatus']) == 'User':
                id_user = request.session['IdUser']
                # получаем список стран, которые пользователь посетил
                countries = user_ops.get_countries_user(id_user)
                # формируем ответ с флагом успешности и списком стран
                result = {'result': True, 'countries': countries}
            else:
                result={'result': False, 'message': 'Неавторизованный вход.'}
        else:
            result={'result': False, 'message': 'Закончилось время сессии.'}
    else:
        result = {'result': False, 'message': 'Не правильный запрос.'}

    # возвращаем результат в JSON формате, с использованием jsonpickle
    # unpicklable=False используется, чтобы не включать метаданные для восстановления объектов Python
    return HttpResponse(jsonpickle.encode(result, unpicklable=False))

# сохранение фото
def save_photo(request):
    if request.method == "POST":
        if Service.check_session(request):
            if str(request.session['UserStatus']) == 'User':
                id_user = request.session['IdUser']
                # Получаем данные из POST-запроса
                id_photo = int(str(request.POST.get('idPhoto')))
                id_country = int(str(request.POST.get('idCountry')))
                photo_base64 = str(request.POST.get('photo'))
                title = str(request.POST.get('title'))
                date = str(request.POST.get('date'))
                description = str(request.POST.get('description'))

                # Обновляем информацию о посещении страны (например, если пользователь впервые добавляет фото,
                # автоматически помечаем страну как "посещенную")
                Service.add_col_des(id_user, id_country)

                # Вызываем метод класса user_ops для сохранения фото в базу данных
                result = user_ops.save_photo(id_photo, id_user, id_country, title, date, description, photo_base64)
            else:
                result={'result': False, 'message': 'Неавторизованный вход.'}
        else:
            result={'result': False, 'message': 'Закончилось время сессии.'}
    else:
        result = {'result': False, 'message': 'Не правильный запрос.'}

    # Возвращаем результат в виде JSON
    return HttpResponse(json.dumps(result))

# загрузка фото пользователя по стране
def load_photos_country(request):
    if request.method == "POST":
        if Service.check_session(request):
            if str(request.session['UserStatus']) == 'User':
                id_user = request.session['IdUser']

                # Получаем ID страны из POST-запроса
                id_country = int(str(request.POST.get('idCountry')))

                # Вызываем метод класса user_ops для получения всех фото пользователя по указанной стране
                result = user_ops.load_photos_country(id_user, id_country)
            else:
                result = {'result': False, 'message': 'Неавторизованный вход.'}
        else:
            result = {'result': False, 'message': 'Закончилось время сессии.'}
    else:
        result = {'result': False, 'message': 'Не правильный запрос.'}

    # Возвращаем JSON с результатом работы метода
    return HttpResponse(json.dumps(result))

# получение данных по фото
def get_photo(request):
    if request.method == "POST":
        if Service.check_session(request):
            if str(request.session['UserStatus']) == 'User':
                id_user = request.session['IdUser']

                # Получаем ID фото из POST-запроса
                id_photo = int(request.POST.get('idPhoto'))

                # Вызываем метод класса user_ops для получения данных конкретного фото
                result = user_ops.get_photo(id_user, id_photo)
            else:
                result = {'result': False, 'message': 'Неавторизованный вход.'}
        else:
            result = {'result': False, 'message': 'Закончилось время сессии.'}
    else:
        result = {'result': False, 'message': 'Не правильный запрос.'}
    return HttpResponse(json.dumps(result))

# удаление фото
def delete_photo(request):
    if request.method == "POST":
        if Service.check_session(request):
            if str(request.session['UserStatus']) == 'User':
                id_user = request.session['IdUser']

                # Получаем ID фото из POST-запроса
                id_photo = int(str(request.POST.get('idPhoto')))

                # Вызываем метод класса user_ops для удаления конкретного фото
                result = user_ops.delete_photo(id_user, id_photo)
            else:
                result={'result': False, 'message': 'Неавторизованный вход.'}
        else:
            result={'result': False, 'message': 'Закончилось время сессии.'}
    else:
        result = {'result': False, 'message': 'Не правильный запрос.'}

    # Возвращаем JSON с результатом операции
    return HttpResponse(json.dumps(result))
