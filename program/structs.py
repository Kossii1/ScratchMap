# СТРУКТУРЫ

# класс описывающий страну
class Country:
    def __init__(self, country_id = 0, name = '', short_name = ''):
        self.country_id = country_id
        self.name = name
        self.short_name = short_name