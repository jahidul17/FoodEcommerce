from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class FoodItem(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, related_name="foods", on_delete=models.CASCADE)
    ingredients = models.TextField(blank=True)
    image = models.ImageField(upload_to="foods/", blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

