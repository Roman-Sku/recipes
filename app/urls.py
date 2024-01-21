from django.urls import path

from .views import create_recipe, show_recipe, update_recipe, create_ingredient

# /recipe/

urlpatterns = [
    path('create/', create_recipe, name='create-recipe'),
    path('update/<int:recipe_id>', update_recipe, name='update-recipe'),
    path('<int:recipe_id>', show_recipe, name='show-recipe'),
    path('create_ingredient', create_ingredient, name='create-ingredient')
]
