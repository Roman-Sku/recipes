from django.contrib.auth import get_user_model
from rest_framework import serializers

from app.models import Recipe, Ingredient


class CategoryField(serializers.ChoiceField):
    def to_representation(self, value: str) -> str:
        for v, label in Recipe.Category.choices:
            if v == value:
                return label
        return "Unknown category"


class ShortUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name"]
        read_only_fields = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    user = ShortUserSerializer(read_only=True)
    category = CategoryField(choices=Recipe.Category.choices)
    v_category = serializers.CharField(source="verbose_category", read_only=True)

    class Meta:
        model = Recipe
        fields = ["id", "name", "preview_image", "description", "created_at", "time_minutes", "ingredients", "category",
                  "user", "v_category"]
        read_only_fields = ["id", "created_at", "user"]
        write_only_fields = ["name", "preview_image", "description", "time_minutes", "ingredients", "category"]

    def create(self, validated_data) -> Recipe:
        # Вытягиваем ключ `ingredients` (удаляем его из `validated_data`)
        ingredients = validated_data.pop("ingredients")

        recipe = Recipe.objects.create(**validated_data)

        ingredients_objects: list[Ingredient] = []
        for ingredient in ingredients:
            obj, created = Ingredient.objects.get_or_create(name=ingredient["name"])
            ingredients_objects.append(obj)

        recipe.ingredients.set(ingredients_objects)

        return recipe


class RecipeListSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    user = ShortUserSerializer(read_only=True)
    category = CategoryField(choices=Recipe.Category.choices)

    class Meta:
        model = Recipe
        fields = ["id", "name", "preview_image", "created_at", "time_minutes", "user", "ingredients", "category"]


class RecipeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ["name", "preview_image", "description", "time_minutes", "ingredients", "category"]


class RecipeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ["id", "name", "preview_image", "description", "created_at", "time_minutes", "ingredients", "category",
                  "user"]


class ImageSerializer(serializers.Serializer):
    image = serializers.ImageField(write_only=True)

    class Meta:
        fields = ["image"]