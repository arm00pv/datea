from django.db import models
class Item(models.Model):
    item_number = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    entry_date = models.DateField(auto_now_add=True)
    expiration_date = models.DateField()

    def __str__(self):
        return self.name

class Subscriber(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
