from django.db import models

class Product(models.Model):
    item_number = models.CharField(max_length=100, unique=True, help_text="UPC or other unique product identifier")
    name = models.CharField(max_length=200)
    total_on_hand = models.IntegerField(default=0)
    weekly_average_sales = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

class Batch(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches')
    quantity = models.IntegerField()
    expiration_date = models.DateField()
    is_steel = models.BooleanField(default=False, help_text="Is the batch in storage?")
    entry_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.name} - Batch expiring on {self.expiration_date}'

class Subscriber(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
