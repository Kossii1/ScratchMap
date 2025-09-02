from django.shortcuts import render
from program.operations import OperationsUser
from program.service import Service
import jsonpickle
import json
from django.http import HttpResponse

user_ops = OperationsUser() # указатель на класс операций пользователя

def welcome_page(request):
    return render(request, 'welcome_page.html')

# авторизация или регистрация
def sign_in_reg(request):
    try:
        select = int(request.POST.get('select', 0))
    except (TypeError, ValueError):
        select = 0
    name = (request.POST.get('name') or '').strip()
    login = (request.POST.get('login') or '').strip()
    password = request.POST.get('password') or ''
    result = user_ops.sign_in_reg(request, select, name, login, password)
    if result.get('result'):
        return show_map(request)
    else:
        return show_info(request, result.get('message'))

# переход на карту
def show_map(request):
    if Service.check_session(request):
        if str(request.session['UserStatus']) == 'User':
            id_user = request.session['IdUser']
            list_my_countries = user_ops.get_countries_user(id_user)
            list_countries = Service.get_countries()
            data = {'ListMyCountries': jsonpickle.encode(list_my_countries, unpicklable=False),
                    'ListCountries': jsonpickle.encode(list_countries, unpicklable=False)}
            return render(request, 'map.html', context=data)

# переход на информационную страницу
def show_info(request, message):
    data = {'info': message}
    return render(request, 'info.html', context=data)

# получение данных по профайлу
def get_profile(request):
    if request.method == "GET":
        if Service.check_session(request):
            if str(request.session['UserStatus']) == 'User':
                id_user = request.session['IdUser']
                result = user_ops.get_profile(id_user)
            else:
                result = {'result': False, 'message:': 'Ошибка.'}
        else:
            result = {'result': False, 'message:': 'Ошибка.'}
    else:
        result = {'result': False, 'message:': 'Ошибка.'}
    return HttpResponse(json.dumps(result))