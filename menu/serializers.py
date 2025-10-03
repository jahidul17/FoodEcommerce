
from rest_framework import serializers
from .models import Category, FoodItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


# class FoodItemSerializer(serializers.ModelSerializer):
#     category = CategorySerializer(read_only=True)
#     category_id = serializers.PrimaryKeyRelatedField(
#         queryset=Category.objects.all(), source="category", write_only=True
#     )

#     class Meta:
#         model = FoodItem
#         fields = ["id", "name", "description", "price", "category", "category_id",
#                   "ingredients", "image", "is_available"]

class FoodItemSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Category.objects.all()
    )

    class Meta:
        model = FoodItem
        fields = '__all__'

