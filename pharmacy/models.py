from django.db import models
from django.utils import timezone

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    category_name = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    item_name = models.CharField(max_length=50, null=True, blank=True)
    unit_price = models.IntegerField(default=0, null=True, blank=True)  # type: ignore
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.item_name

    def get_total_value(self):
        """Calculate total value of current stock (sum of all batches)"""
        return sum(batch.quantity * self.unit_price for batch in self.batches.all())  # type: ignore


class Sale(models.Model):
    item = models.ForeignKey(Product, on_delete=models.CASCADE)  # type: ignore
    quantity = models.IntegerField(default=0, null=True, blank=True)  # type: ignore
    amount_received = models.IntegerField(default=0, null=True, blank=True)  # type: ignore
    issued_to = models.CharField(max_length=50, null=True, blank=True)
    unit_price = models.IntegerField(default=0, null=True, blank=True)  # type: ignore
    date_created = models.DateTimeField(default=timezone.now)

    def get_total(self):
        """Calculate total cost of the sale"""
        total = self.quantity * self.unit_price  # type: ignore
        return int(total)

    def get_change(self):
        """Calculate change given to customer"""
        change = self.amount_received - self.get_total()  # type: ignore
        return abs(int(change))

    def __str__(self):
        return f"{self.item.item_name} - {self.issued_to} ({self.date_created.strftime('%Y-%m-%d')})"  # type: ignore


class MedicineBatch(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches')  # type: ignore
    batch_number = models.CharField(max_length=50, null=True, blank=True)
    manufacture_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    quantity = models.IntegerField(default=0)  # type: ignore

    def __str__(self):
        return f"{self.product.item_name} (Batch: {self.batch_number or 'N/A'}) - Exp: {self.expiry_date}"  # type: ignore