from django.db import models
from datetime import date

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

    @property
    def days_to_expiration(self):
        return (self.expiration_date - date.today()).days

    @property
    def predicted_sales_until_expiration(self):
        if self.days_to_expiration > 0:
            # Ensure weekly_average_sales is not zero to avoid division by zero
            if self.product.weekly_average_sales > 0:
                return (self.product.weekly_average_sales / 7) * self.days_to_expiration
        return 0

    @property
    def is_at_risk(self):
        """
        A batch is at risk if its quantity is greater than the predicted sales
        before expiration. If the batch is already expired, it's considered
        at risk if there's any quantity left.
        """
        if self.days_to_expiration > 0:
            return self.quantity > self.predicted_sales_until_expiration
        else:
            return self.quantity > 0

    def __str__(self):
        return f'{self.product.name} - Batch expiring on {self.expiration_date}'

class Subscriber(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
