// СКРИПТЫ НАЧАЛЬНОЙ СТРАНИЦЫ
var Select = 1; // что выбрали, 1 - авторизация, 2 - регистрация

// событие при окончании загрузки страницы
$(window).on('load', function() {
    select_auth();
});

// что выбрали, авторизацию
function select_auth(){
    document.getElementById('signIn').checked = true;
    document.getElementById('reg').checked = false;
    document.getElementById('tdName').style.display = 'none';
    Select = 1;
}

// что выбрали, регистрацию
function select_reg(){
    document.getElementById('signIn').checked = false;
    document.getElementById('reg').checked = true;
    document.getElementById('tdName').style.display = 'block';
    Select = 2;
}

// нажата кнопка перехода на карту
function go_map(){
    var name = '';
    // Если выбрана регистрация проверяем никнейм
    if(Select == 2){
        name = document.getElementById('name').value;
        if(name.length < 3){
            alert('Никнейм должен состоять минимум из 3 символов.');
            return;
        }
    }
    var login = document.getElementById('login').value;
    if(login.length < 5){
        alert('Логин должен состоять минимум из 5 символов.');
        return;
    }
    var password = document.getElementById('password').value;
    if(password.length < 5){
        alert('Пароль должен состоять минимум из 5 символов.');
        return;
    }
    // Добавляем выбор пользователя в форму перед отправкой
    document.querySelector('input[name="select"]').value = Select;
    document.getElementById('authForm').submit();
}