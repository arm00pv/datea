from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_number = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    entry_date = models.DateField(auto_now_add=True)
    expiration_date = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'item_number'], name='unique_item_per_user')
        ]

    def __str__(self):
        return self.name
