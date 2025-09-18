# СТРУКТУРЫ

# класс описывающий страну
class Country:
    def __init__(self, country_id = 0, name = '', short_name = ''):
        self.country_id = country_id
        self.name = name
        self.short_name = short_name

# класс описывающий посещенную страну пользователем
class MyCountry:
    def __init__(self, country = Country, description = '', color_select = '', list_id_photos = None):
        self.country = country
        self.description = description
        self.color_select = color_select
        self.list_id_photos = list_id_photos
