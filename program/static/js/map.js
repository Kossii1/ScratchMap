// СКРИПТЫ КАРТЫ
var Map, ScreenWidth, ScreenHeight, PanelControl, WidthPanelControl = 300, DarkLayer;
var ModalWin, ModalSubWin;
var NameSelectCountry; // наименование выделенной страны
var ShortNameCountry; // сокращенное название страны, как RU, US
var Regions;

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

    Map.geoObjects.events.add('click', function(e) {
        // определяем полигон, в который кликнули, и координаты клика
        let regClicked = e.get('target'), coords = e.get('coords');
        // открываем балун с названием страны в точке клика
        //regClicked.properties.set('balloonContent', regClicked.properties.get('name'));
        //regClicked.balloon.open(coords);
        NameSelectCountry = regClicked.properties.get('name');
        ShortNameCountry = regClicked.properties.get('iso3166');
        selectColorCountries();
        setInfoCountry();
        showListCountries();
    });
    showListCountries();
    selectColorCountries();
}

// выделение стран заданным цветом
function selectColorCountries(){
    Map.geoObjects.removeAll();
    // отображение границ стран
    ymaps.borders.load('001').then(function (geojson) {
        regions = ymaps.geoQuery(geojson);
        regions.addToMap(Map);
    });
    // выделение стран заданным цветом
    ymaps.borders.load('001', {
        lang: 'ru',
        quality: 1
    }).then(function(geojson) {
        var regions = ymaps.geoQuery(geojson);
        var checkSelect = false;
        for(var i=0;i<ListMyCountries.length;i++){
            var country = ListMyCountries[i];
            var region = regions.search('properties.iso3166 = "' + country.country.short_name + '"');
            region.setOptions('fillColor', country.colorSelect);
            region.setOptions('fillOpacity', 0.6);
            if(country.country.name === NameSelectCountry){
                region.setOptions('strokeColor', '#fc021a');
                region.setOptions('strokeWidth', 2);
                checkSelect = true;
            }
            region.addToMap(Map);
        }
        if(checkSelect == false){
            var region = regions.search('properties.iso3166 = "' + ShortNameCountry + '"');
            region.setOptions('strokeColor', '#fc021a');
            region.setOptions('strokeWidth', 2);
            region.addToMap(Map);
        }
    });
}

// установка списка стран
function showListCountries(){
    var div, table, row, cell, label, topPos = 0;
    div = document.getElementById('divCountries');
    div.innerHTML = '';
    table = document.createElement('table');
    table.setAttribute('cellpadding', '0');
    table.setAttribute('cellspacing', '0');
    table.setAttribute('width', '100%');
    for(i=0;i<ListCountries.length;i++){
        row = table.insertRow();
        cell = row.insertCell();
        label = document.createElement('label');
        if(ListCountries[i].name == NameSelectCountry){
            label.className = 'text6';
            topPos = i * 20;
        }
        else label.className = 'text5';
        label.innerHTML = ListCountries[i].name;
        label.name = ListCountries[i].name;
        label.short_name = ListCountries[i].short_name;
        label.addEventListener("click",
            function(){
                NameSelectCountry = this.name;
                ShortNameCountry = this.short_name;
                selectColorCountries();
                setInfoCountry();
                showListCountries();
            }, false);
        cell.append(label);
    }
    div.appendChild(table);
    div.scrollTop = topPos;
}

// установка инфо о стране
function setInfoCountry() {
    document.getElementById('nameSelectCountry').innerHTML = NameSelectCountry;

    var url = `https://restcountries.com/v3.1/alpha/${ShortNameCountry}`;

    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error('Country not found');
            return response.json();
        })
        .then(data => {
            var countryData = data[0];

            var nameRu = countryData.translations?.rus?.official || countryData.name.official;

            var capital = countryData.capital ? countryData.capital[0] : "—";

            var currencies = [];
            if (countryData.currencies) {
                var allCurrencies = Object.values(countryData.currencies);
                currencies = allCurrencies.slice(0, 3).map(c => c.name + (c.symbol ? ` (${c.symbol})` : ""));
            }

            var languages = [];
            if (countryData.languages) {
                var allLanguages = Object.values(countryData.languages);
                languages = allLanguages.slice(0, 3);
            }

            var text = 'Полное название: ' + nameRu +
                       '<br>Столица: ' + capital +
                       '<br>Валюта: ' + (currencies.length ? currencies.join(", ") : "—") +
                       '<br>Языки: ' + (languages.length ? languages.join(", ") : "—");

            var check = false;
            for (var i = 0; i < ListMyCountries.length; i++) {
                var country = ListMyCountries[i];
                if (country.country.short_name == countryData.cca2) { // сверка по ISO2
                    check = true;
                    break;
                }
            }
            text += check ? '<br>Посещение: да' : '<br>Посещение: нет';

            document.getElementById('dataCountry').innerHTML = text;
            document.getElementById('tdPhotosCountry').style.display = 'block';
            document.getElementById('tdAttendance').style.display = 'block';
        })
        .catch(error => console.log("error", error));
}

// показать профиль
function showProfile(){
    $.ajax({
        type:"GET",
        url: "/get_profile/",
        data:{},
        success: function(data){
            var dataJson = JSON.parse(data);
            if(dataJson.result){
                document.getElementById('nameProfile').value = dataJson.name;
                document.getElementById('loginProfile').value = dataJson.login;
                document.getElementById('passwordProfile').value = dataJson.password;
                openModal('modal_profile');
            }else alert(dataJson.message);
        },
        error: function(jqXHR, textStatus, errorThrown){
            alert('Произошла ошибка.');
        }
    })
}

// открытие модального окна
function openModal(name_modal){
	DarkLayer = document.createElement('div');
    DarkLayer.id = 'shadow';
    document.body.appendChild(DarkLayer);
	ModalWin = document.getElementById(name_modal);
	ModalWin.style.display = 'block';
}

// закрытие модального окна
function closeModal(){
    DarkLayer.parentNode.removeChild(DarkLayer);
    ModalWin.style.display = 'none';
}


