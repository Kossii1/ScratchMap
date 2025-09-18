from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    login = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)

    class Meta:
        db_table = 'users'


class Country(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=10)

    class Meta:
        db_table = 'countries'


class Photo(models.Model):
    id = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='id_user')
    id_country = models.ForeignKey(Country, on_delete=models.CASCADE, db_column='id_country')
    title = models.CharField(max_length=300)
    date = models.DateField()
    description = models.TextField(max_length=5000)
    image = models.TextField()

    class Meta:
        db_table = 'photos'


class ColorCountry(models.Model):
    id = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='id_user')
    id_country = models.ForeignKey(Country, on_delete=models.CASCADE, db_column='id_country')
    color = models.CharField(max_length=45)

    class Meta:
        db_table = 'colorCountries'


class DescriptionCountry(models.Model):
    id = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='id_user')
    id_country = models.ForeignKey(Country, on_delete=models.CASCADE, db_column='id_country')
    description = models.TextField(max_length=5000)

    class Meta:
        db_table = 'descriptionCountries'