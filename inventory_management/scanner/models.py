from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('user', 'name',)

    def __str__(self):
        return self.name

class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    item_number = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    entry_date = models.DateField(auto_now_add=True)
    expiration_date = models.DateField()

    class Meta:
        unique_together = ('user', 'item_number',)

    def __str__(self):
        return self.name

class Subscriber(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
