from django.urls import path

from . import views

# /api/food/

app_name = 'food:api'

urlpatterns = [
    # Классы представлений указываем через вызов метода `as_view`
    path("", views.RecipeListCreateAPIView.as_view(), name="food-list-create"),
    path("<int:pk>", views.RecipeDetailAPIView.as_view(), name="recipe"),
    path("image", views.UploadImageAPIView.as_view(), name="recipe-image-upload"),
]