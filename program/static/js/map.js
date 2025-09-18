// СКРИПТЫ ГЛАВНОЙ СТРАНИЦЫ
// Глобальные переменные
var Map, DarkLayer;
var ModalWin, ModalSubWin;
var NameSelectCountry; // наименование выделенной страны
var ShortNameCountry; // сокращенное название страны, как RU, US

ymaps.ready(init);
function init(){

    // инициализируем карту,
    Map = new ymaps.Map('map', {
        center: [42.0, 34.0],
        zoom: 2.4,
        type: 'yandex#map',
        controls: ['zoomControl'],
    },{
    });

    // Обработка клика по стране
    Map.geoObjects.events.add('click', function(e) {
        let regClicked = e.get('target'), coords = e.get('coords');
        NameSelectCountry = regClicked.properties.get('name');
        ShortNameCountry = regClicked.properties.get('iso3166');
        selectColorCountries();
        setInfoCountry();
        showListCountries();
    });

    // Первичное построение списка и закраски стран
    showListCountries();
    selectColorCountries();
}

// выделение стран заданными цветами
function selectColorCountries(){
    Map.geoObjects.removeAll();

    // Сначала отрисовываем все границы стран
    ymaps.borders.load('001').then(function (geojson) {
        regions = ymaps.geoQuery(geojson);
        regions.addToMap(Map);
    });

    // Далее выделяем страны из списка пользователя
    ymaps.borders.load('001', {
        lang: 'ru',
        quality: 1
    }).then(function(geojson) {
        var regions = ymaps.geoQuery(geojson);
        var checkSelect = false;
        for(var i=0;i<ListMyCountries.length;i++){
            var country = ListMyCountries[i];
            var region = regions.search('properties.iso3166 = "' + country.country.short_name + '"');

            // закрашиваем страну индивидуальным цветом
            region.setOptions('fillColor', country.color_select);
            region.setOptions('fillOpacity', 0.6);

            // если именно эта страна выбрана — выделяем её красной рамкой
            if(country.country.name === NameSelectCountry){
                region.setOptions('strokeColor', '#fc021a');
                region.setOptions('strokeWidth', 2);
                checkSelect = true;
            }
            region.addToMap(Map);
        }

        // Если выбрана страна, которая не была посещена выделяем её красной рамкой
        if(checkSelect == false){
            var region = regions.search('properties.iso3166 = "' + ShortNameCountry + '"');
            region.setOptions('strokeColor', '#fc021a');
            region.setOptions('strokeWidth', 2);
            region.addToMap(Map);
        }
    });
}

// Построение списка всех стран
function showListCountries() {
    let div = document.getElementById('divCountries');
    div.innerHTML = '';

    // создаём список без стандартного оформления браузера:
    // убираем маркеры, отступы и поля, чтобы полностью управлять стилями через CSS
    let ul = document.createElement('ul');
    ul.style.listStyle = 'none';
    ul.style.padding = '0';
    ul.style.margin = '0';

    let topPos = 0;

    for (let i = 0; i < ListCountries.length; i++) {
        let li = document.createElement('li');
        let label = document.createElement('label');

        // выделяем выбранную страну другим стилем
        if (ListCountries[i].name === NameSelectCountry) {
            label.className = 'text3';
            topPos = i * 20;
        } else {
            label.className = 'text2';
        }

        // сохраняем в элементе название и ISO-код
        label.textContent = ListCountries[i].name;
        label.dataset.name = ListCountries[i].name;
        label.dataset.shortName = ListCountries[i].short_name;

        // обработчик клика по названию страны
        label.addEventListener("click", function () {
            // обновляем выбранную страну
            NameSelectCountry = this.dataset.name;
            ShortNameCountry = this.dataset.shortName;

            // обновляем карту, инфо-блок и сам список
            selectColorCountries();
            setInfoCountry();
            showListCountries();
        });

        li.appendChild(label);
        ul.appendChild(li);
    }

    // добавляем готовый список в контейнер
    div.appendChild(ul);
    div.scrollTop = topPos;
}

// Поиск страны в списке по названию
function findCountry() {
    // получаем значение из поля поиска и обрабатываем пустую строку
    let input = document.getElementById('findCountryInput').value;
    if (!input) {
        alert('Введите название страны.');
        return;
    }

    input = input.toLowerCase();

    // ищем первую страну, которая начинается с введённого текста
    let country = ListCountries.find(c =>
        c.name.toLowerCase().startsWith(input)
    );

    // если совпадений нет — предупреждаем
    if (!country) {
        alert('Ничего не найдено.');
        return;
    }

    // если нашли — обновляем текущую выбранную страну
    NameSelectCountry = country.name;
    ShortNameCountry = country.short_name;

    // обновляем карту, информационный блок и список стран
    selectColorCountries();
    setInfoCountry();
    showListCountries();
}

// установка инфо о стране
function setInfoCountry() {
    document.getElementById('nameSelectCountry').innerHTML = NameSelectCountry;

    // формируем API-запрос к restcountries по ISO-коду страны
    var url = `https://restcountries.com/v3.1/alpha/${ShortNameCountry}`;

    // отправляем запрос
    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error('Country not found');
            return response.json();
        })
        .then(data => {
            var countryData = data[0];

            // официальное название на русском (если есть) или дефолтное
            var nameRu = countryData.translations?.rus?.official || countryData.name.official;

            // столица (если в API отсутствует — ставим прочерк)
            var capital = countryData.capital ? countryData.capital[0] : "—";

            // валюты (берём максимум 3, формат: "доллар (USD)")
            var currencies = [];
            if (countryData.currencies) {
                var allCurrencies = Object.values(countryData.currencies);
                currencies = allCurrencies.slice(0, 3).map(c => c.name + (c.symbol ? ` (${c.symbol})` : ""));
            }

            // языки (берём максимум 3)
            var languages = [];
            if (countryData.languages) {
                var allLanguages = Object.values(countryData.languages);
                languages = allLanguages.slice(0, 3);
            }

            // собираем текстовую инфу о стране
            var text = 'Полное название: ' + nameRu +
                       '<br>Столица: ' + capital +
                       '<br>Валюта: ' + (currencies.length ? currencies.join(", ") : "—") +
                       '<br>Языки: ' + (languages.length ? languages.join(", ") : "—");

            // проверяем, есть ли страна в списке посещённых (ListMyCountries)
            var check = false;
            for (var i = 0; i < ListMyCountries.length; i++) {
                var country = ListMyCountries[i];
                if (country.country.short_name == countryData.cca2) { // сверка по ISO2
                    check = true;
                    break;
                }
            }
            // добавляем строку о посещении
            text += check ? '<br>Посещение: да' : '<br>Посещение: нет';

            // выводим результат в DOM
            document.getElementById('dataCountry').innerHTML = text;

            // делаем блоки с отметкой о посещении и ссылкой на Википедию видимыми
            document.getElementById('WikiCountry').style.display = 'block';
            document.getElementById('tdAttendance').style.display = 'block';
        })
        .catch(error => console.log("error", error));
}

// показать профиль
function showProfile(){
    $.ajax({
        type:"GET",                // метод запроса — берём данные с сервера
        url: "/get_profile/",
        data:{},
        success: function(data){
            // сервер вернул строку → парсим её в JSON
            var dataJson = JSON.parse(data);
            if(dataJson.result){
                // заполняем поля формы профиля полученными данными
                document.getElementById('nameProfile').value = dataJson.name;
                document.getElementById('loginProfile').value = dataJson.login;

                // открываем модальное окно с профилем
                openModal('modal_profile');
            }else alert(dataJson.message);
        },
        error: function(jqXHR, textStatus, errorThrown){
            alert('Произошла ошибка.');
        }
    })
}

// сохранить профиль
function saveProfile(){
    var name, login, password;

    // получаем значения из полей формы
    name = document.getElementById('nameProfile').value;
    login = document.getElementById('loginProfile').value;
    password = document.getElementById('passwordProfile').value;

    // проверки валидации
    if(name.length < 3){
        alert('Никнейм должен состоять минимум из 3 символов.');
        return;
    }
    if(login.length < 5){
        alert('Логин должен состоять минимум из 5 символов.');
        return;
    }
    // если новый пароль введен, должен быть не меньше 5 символов
    if(password.length < 5 && password.length > 0){
        alert('Пароль должен состоять минимум из 5 символов.');
        return;
    }
    // запрос к серверу
    $.ajax({
        type:"POST",
        url: "/save_profile/",
        headers: {'X-CSRFToken': CsrfToken},
        data:{
            name: name,
            login: login,
            password: password
        },
        success: function(data){

            // сервер вернул строку → парсим в JSON
            var dataJson = JSON.parse(data);

            // если сохранение успешно, если сервер вернул ошибку — показываем её
            if(dataJson.result){
                alert('Сохранение профиля прошло успешно.');
            }else alert(dataJson.message);
        },
        error: function(jqXHR, textStatus, errorThrown){
            alert('Произошла ошибка.');
        }
    })

    // очищаем поле пароля после сохранения (безопасность)
    document.getElementById('passwordProfile').value = '';
}

// выход из аккаунта
function exitProfile(){
    // спрашиваем пользователя для подтверждения выхода
    var isClose = confirm('Выйти из аккаунта?');

    // если пользователь подтвердил
    if(isClose){
        $.ajax({
            type:"GET",
            url: "/exit_profile/",
            data:{},
            success: function(data){
                var dataJson = JSON.parse(data);
                // если выход прошёл успешно, перенаправляем пользователя на главную страницу
                if(dataJson.result){
                    window.open('/', '_self');
                }else alert(dataJson.message);
            },
            error: function(jqXHR, textStatus, errorThrown){
                alert('Произошла ошибка.');
            }
        })
    }
}

// переход на статью страны в Википедии
function goWikiCountry(){
    // формируем URL статьи на русском языке
    // encodeURIComponent используется для безопасного кодирования названия страны в URL
    window.open(
        'https://ru.wikipedia.org/wiki/' + encodeURIComponent(NameSelectCountry),
        '_blank'
    );
}

var ColorCountryEl = document.getElementById('colorCountry');
var DescriptionCountryEl = document.getElementById('descriptionCountry');

// добавить или изменить посещаемость
function addEditAttendance(){
    // меняем заголовок модального окна с указанием выбранной страны
    document.getElementById('title_attendance').innerHTML = 'Посещение страны ' + NameSelectCountry;

    // ищем страну в списке посещённых стран пользователя
    const foundCountry = ListMyCountries.find(myCountry => myCountry.country.short_name === ShortNameCountry);

    if (foundCountry) {
        // если страна уже была посещена → заполняем поля модального окна текущими данными
        ColorCountryEl.value = foundCountry.color_select;
        DescriptionCountryEl.value = foundCountry.description;
    } else {
        // если страна ещё не отмечена → устанавливаем значения по умолчанию
        ColorCountryEl.value = '#6e87f2';
        DescriptionCountryEl.value = '';
    }
    // загружаем фотографии для выбранной страны
    loadPhotosCountry();

    // открываем модальное окно для редактирования посещения
    openModal('modal_attendance');
}

// сохранение цвета и впечатления от страны
function saveColDesCountry(){
    var color, description, idCountry;

    // ищем объект страны по короткому коду ISO
    const country = ListCountries.find(c => c.short_name === ShortNameCountry);
    idCountry = country.country_id;

    // получаем данные из модального окна
    color = ColorCountryEl.value;
    description = DescriptionCountryEl.value;

    // отправляем AJAX-запрос на сервер для сохранения информации
    $.ajax({
        type:"POST",
        url: "/save_col_des_country/",
        headers: {'X-CSRFToken': CsrfToken},
        data:{
            idCountry: idCountry,
            color: color,
            description: description
        },
        success: function(data){
            // парсим JSON-ответ от сервера
            var dataJson = JSON.parse(data);

            // Если сохранение прошло успешно
            if(dataJson.result){
                // обновляем список стран пользователя после успешного сохранения
                getMyCountries();
                // обновляем информацию о выбранной стране в интерфейсе
                setInfoCountry();
                alert('Сохранение прошло успешно.');
            }else alert(dataJson.message);
        },
        error: function(jqXHR, textStatus, errorThrown){
            alert('Произошла ошибка.');
        }
    })
}

// получение инфы о странах посещенных пользователем
function getMyCountries(){
    $.ajax({
        type:"GET",     // используем GET, так как только получаем данные
        url: "/get_user_countries/",
        data:{},
        success: function(data){
            // сервер вернул JSON в виде строки → парсим в объект
            var dataJson = JSON.parse(data);

            // Если данные получены успешно сохраняем
            if(dataJson.result){
                // обновляем глобальный список посещённых стран пользователя
                ListMyCountries = dataJson.countries;

                // обновляем отображение карты с выделением стран
                selectColorCountries();
            }else alert(dataJson.message);
        },
        error: function(jqXHR, textStatus, errorThrown){
            alert('Произошла ошибка.');
        }
    })
}

var IdPhoto = 0; // глобальная переменная: если 0 → добавление нового фото, иначе редактирование существующего
var ImageBase64 = null; // загруженный файл в формате base64
// открытие модального окна для добавления и изменения фото
function showAddEditPhoto(idPhoto){
    IdPhoto = idPhoto;

    // редактирование существующего фото
    if(idPhoto > 0){
        $.ajax({
        type:"POST",        // POST используется для безопасной передачи данных
        url: "/get_photo/",
        headers: {'X-CSRFToken': CsrfToken},
        data:{
            idPhoto: idPhoto
        },
        success: function(data){
            // парсим JSON-ответ
            var dataJson = JSON.parse(data);

            // Если редактирование прошло успешно
            if(dataJson.result){
                var photoEl = document.getElementById('photo');
                var photo = dataJson.photo;

                // сохраняем изображение в base64 для дальнейшей работы
                ImageBase64 = photo.image;

                // создаём объект Image для корректного расчёта высоты
                var image = new Image();
                image.src = "data:image/gif;base64," + ImageBase64;

                // ограничиваем высоту фото в модальном окне 300px
                if(image.height > 300) photoEl.style.height = 300 + 'px';
                else photoEl.style.height = this.height + 'px';
                photoEl.src = "data:image/gif;base64," + ImageBase64;

                // заполняем поля форму данными из базы
                document.getElementById('titlePhotoAD').value = photo.title;
                document.getElementById('datePhotoAD').value = photo.date;
                document.getElementById('descriptionPhotoAD').value = photo.description;
            }else alert(dataJson.message);  // ошибка от сервера
        },
        error: function(jqXHR, textStatus, errorThrown){
            alert('Произошла ошибка.');
        }
    })
    }else{  // добавление нового фото
        // очищаем все поля формы
        document.getElementById('photo').src = '';
        document.getElementById('titlePhotoAD').value = '';
        document.getElementById('datePhotoAD').value = '';
        document.getElementById('descriptionPhotoAD').value = '';
        ImageBase64 = null; // сбрасываем временное хранилище изображения
    }

    // открываем дополнительное модальное окно для добавления/редактирования фото
    openSubModal('modal_add_edit_photo');
}

// открытие диалога выбора файла для загрузки фото
function addPhoto(){
    // "кликаем" по скрытому input type="file", чтобы открыть стандартное окно выбора файла
    document.getElementById('file_input').click();
}

// обработка выбранного файла
function downloadFile(file){
    var photoEl = document.getElementById('photo'); // элемент <img> для превью
    const reader = new FileReader();    // объект для чтения файлов в JS
    reader.onload = (e) => {
        // убираем метаданные из результата, оставляем только Base64-код
        ImageBase64 = reader.result.replace(/^data:image\/[a-z]+;base64,/, ''); // убираем метаданные из изображения

        var image = new Image();    // создаём объект Image для расчёта размеров
        image.src = reader.result;  // src с метаданными нужен для корректного отображения

        image.onload = function() {
            // ограничиваем высоту превью до 300px
            if(this.height > 300) photoEl.style.height = 300 + 'px';
            else photoEl.style.height = this.height + 'px';

            // отображаем изображение в <img> превью
            photoEl.src = "data:image/gif;base64," + ImageBase64;
        };
    };
    // читаем файл как Data URL
    reader.readAsDataURL(file[0]);
}

// сохранение фото
function savePhoto(){
    var title, date, description, idCountry;

    // ищем объект страны по выбранному короткому коду ISO
    const country = ListCountries.find(c => c.short_name === ShortNameCountry);
    idCountry = country.country_id;

    // получаем значения из полей формы модального окна
    title = document.getElementById('titlePhotoAD').value;
    date = document.getElementById('datePhotoAD').value;
    description = document.getElementById('descriptionPhotoAD').value;

    // валидация: проверяем, что изображение выбрано
    if(ImageBase64 == null){
        alert('Не выбрано изображение.');
        return;
    }
    // проверяем, что указан заголовок
    if(title.length == 0){
        alert('Укажите заголовок.');
        return;
    }
    // проверяем, что указана дата
    if(date == ''){
        alert('Укажите дату.');
        return;
    }
    // AJAX-запрос к серверу
    $.ajax({
        type:"POST",    // используем POST, т.к. передаются данные
        url: "/save_photo/",
        headers: {'X-CSRFToken': CsrfToken},
        data:{
            idPhoto: IdPhoto,
            idCountry: idCountry,
            photo: ImageBase64,
            title: title,
            date: date,
            description: description
        },
        success: function(data){
            // парсим JSON ответ сервера
            var dataJson = JSON.parse(data);

            // если сервер подтвердил успешное сохранение
            if(dataJson.result){
                getMyCountries();   // обновляем список посещённых стран
                loadPhotosCountry();    // обновляем список фото страны
                alert('Фото успешно загружено.');
                closeSubModal();    // закрываем модальное окно
            }else alert(dataJson.message);  // ошибка от сервера
        },
        error: function(jqXHR, textStatus, errorThrown){
            alert('Произошла ошибка.');
        }
    })
}

var ListDataImagesCountry = []; // глобальный массив для хранения фото выбранной страны
// загрузка фото определенной страны у пользователя
function loadPhotosCountry(){
    // очищаем предыдущий список фото, чтобы загрузить свежие данные
    ListDataImagesCountry = [];

    // находим объект страны по короткому коду ISO
    const country = ListCountries.find(c => c.short_name === ShortNameCountry);
    var idCountry = country.country_id;

    // AJAX-запрос к серверу для получения фото выбранной страны
    $.ajax({
        type:"POST",    // используем POST для передачи данных
        url: "/load_photos_country/",
        headers: {'X-CSRFToken': CsrfToken},
        data:{
            idCountry: idCountry    // передаём id страны
        },
        success: function(data){
            // парсим JSON-ответ сервера
            var dataJson = JSON.parse(data);

            // если сервер вернул успешный результат
            if(dataJson.result){
                var photos = dataJson.photos;

                // сохраняем все фото в глобальный массив для дальнейшего отображения
                for(var i=0;i<photos.length;i++)
                    ListDataImagesCountry.push(photos[i]);

                // отображаем фотографии в модальном окне посещения
                showPhotosCountry();
            }else alert(dataJson.message);  // если ошибка, показываем сообщение
        },
        error: function(jqXHR, textStatus, errorThrown){
            alert('Произошла ошибка.');
        }
    })
}

// отображение фотографий в модальном окне посещения
function showPhotosCountry() {
    const div = document.getElementById('divPhotosCountry');
    div.innerHTML = '';

    // перебираем все фото выбранной страны
    ListDataImagesCountry.forEach(photo => {
        const item = document.createElement('div');
        item.className = 'photo-item';  // обёртка для каждой карточки фото

        // создание элемента изображения
        const imgPhoto = document.createElement('img');
        imgPhoto.className = 'photo';
        imgPhoto.src = "data:image/gif;base64," + photo.image;  // отображаем фото в формате base64
        imgPhoto.dataset.idPhoto = photo.id;    // сохраняем id фото в dataset
        imgPhoto.addEventListener("click", () => {
            showAddEditPhoto(imgPhoto.dataset.idPhoto); // при клике открываем модальное окно для редактирования
        });

        // блок с текстовой информацией
        const info = document.createElement('div');
        info.className = 'info';

        // заголовок + дата
        const titleDate = document.createElement('div');
        titleDate.className = 'title-date';
        titleDate.textContent = photo.title.length > 70 ? photo.title.substring(0, 70) + "..." : photo.title;
        titleDate.textContent += " | " + photo.date;

        // описание
        const description = document.createElement('div');
        description.className = 'description';
        description.textContent = photo.description.length > 150 ? photo.description.substring(0, 150) + "..." : photo.description;

        info.append(titleDate, description);

        // кнопка удаления фото
        const imgDelete = document.createElement('img');
        imgDelete.className = 'delete';
        imgDelete.src = '/static/img/close.gif';
        imgDelete.title = 'Удалить';
        imgDelete.dataset.idPhoto = photo.id;   // сохраняем id фото в атрибуте data-idPhoto для использования при удалении

        // добавляем обработчик клика по кнопке
        imgDelete.addEventListener("click", () => {
            if (confirm('Удалить изображение?')) {  // подтверждение действия у пользователя
                // AJAX-запрос на сервер для удаления фото
                $.ajax({
                    type: "POST",
                    url: "/delete_photo/",
                    headers: {'X-CSRFToken': CsrfToken},
                    data: { idPhoto: imgDelete.dataset.idPhoto },   // передаём id фото на сервер
                    success: function(data) {
                        const dataJson = JSON.parse(data);

                        // если удаление прошло успешно
                        if (dataJson.result) {
                            getMyCountries();   // обновляем список стран пользователя
                            loadPhotosCountry();    // перезагружаем фото для выбранной страны
                        }else alert(dataJson.message);  // если ошибка, показываем сообщение
                    },
                    error: function() {
                        alert('Произошла ошибка.');
                    }
                });
            }
        });

        // собираем карточку
        item.append(imgPhoto, info, imgDelete);
        div.appendChild(item);  // добавляем в контейнер
    });
}

// открытие модального окна прогресса посещения мира
function showProgress(){
     // считаем общее количество стран и количество посещённых
	var allCountries = ListCountries.length;
	var myCountries = ListMyCountries.length;

	// вычисляем проценты посещённых и непосещённых стран
	var percentMy = myCountries / allCountries * 100.0;
	var percentOther = 100.0 - percentMy;

	// данные для диаграммы (Chart.js)
	const coursesData = {
		labels: ['Посещенные страны ' + percentMy.toFixed(2) + '%', 'Непосещенные страны ' + percentOther.toFixed(2) + '%'],
		datasets: [{
			data: [percentMy, percentOther],    // значения для сегментов
			backgroundColor: ['#FF6384', '#36A2EB'],    // цвета сегментов
		}],
	};

	// конфигурация диаграммы
	const config = {
		type: 'doughnut',   // тип диаграммы: круговая "пончик"
		data: coursesData,
		options: {
			plugins: {
				title: {
					display: true,
					text: '',
				},
			},
		},
	};

	// создаём диаграмму в canvas с id "chartProgress"
	const ctx = document.getElementById('chartProgress').getContext('2d');
	new Chart(ctx, config);

	// формируем список посещённых стран с количеством фото
	var div = document.getElementById('divMyCountries');
    div.innerHTML = '';

    var ul = document.createElement('ul');
    ul.className = 'my-countries-list'; // класс для стилизации списка

    // заполняем список данными
    for (var i = 0; i < ListMyCountries.length; i++) {
        var li = document.createElement('li');
        li.className = 'text7';
        li.textContent = ListMyCountries[i].country.name + ', фото - ' + ListMyCountries[i].listIdPhotos.length + ' шт.';
        ul.appendChild(li);
    }
    div.appendChild(ul);    // добавляем список в DOM
    // открываем модальное окно с диаграммой и списком
	openModal('modal_progress_diagram');
}

// экспорт карты в jpg
function exportMap(){
    // используем библиотеку html2canvas для "снимка" карты
    html2canvas(document.getElementById('map')).then(canvas => {

        // создаём ссылку для скачивания
        const link = document.createElement('a');
        link.download = 'map.png';  // имя файла при сохранении
        link.href = canvas.toDataURL('image/png');
        link.click();   // инициируем скачивание файла
    });
}

// открытие модального окна
function openModal(name_modal){
    // создаём тёмный фон (оверлей) для затемнения остальной страницы
	DarkLayer = document.createElement('div');
    DarkLayer.id = 'shadow';
    document.body.appendChild(DarkLayer);   // добавляем его в DOM

    // находим нужное модальное окно по имени
	ModalWin = document.getElementById(name_modal);
	// отображаем модальное окно
	ModalWin.style.display = 'block';
}

// закрытие модального окна
function closeModal(){
    // удаляем тёмный фон с DOM и скрываем модальное окно
    DarkLayer.parentNode.removeChild(DarkLayer);
    ModalWin.style.display = 'none';
}

// открытие дополнительного модального окна
function openSubModal(name_modal){
    // находим элемент модального окна по его имени и делаем его видимым
	ModalSubWin = document.getElementById(name_modal);
	ModalSubWin.style.display = 'block';
}

// закрытие дополнительного модального окна
function closeSubModal(){
    // скрываем окно, меняя display на 'none'
    ModalSubWin.style.display = 'none';
}
