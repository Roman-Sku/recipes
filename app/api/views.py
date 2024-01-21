from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.serializers import ModelSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

from app.models import Recipe
from .permissions import IsOwnerOrReadOnly
from .serializers import RecipeListSerializer, RecipeCreateSerializer, RecipeDetailSerializer, RecipeSerializer, ImageSerializer


class RecipeListCreateAPIView(ListCreateAPIView):
    """
    Класс API view, для endpoint'a просмотра перечня рецептов и создания новых.
    """
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]  # Реагирует на (query) параметр `search`
    search_fields = ['@name', '@description']  # Используем полнотекстовый поиск Postgres
    ordering_fields = ["created_at", "time_minutes", "user_username"]
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        """В зависимости от метода HTTP возвращает соответствующий класс для создания сериализатора"""
        if self.request.method == 'POST':
            return RecipeSerializer
        return RecipeListSerializer

    def perform_create(self, serializer):
        """Во время создания рецепта добавляем владельца"""
        serializer.save(user=self.request.user)


class RecipeDetailAPIView(RetrieveUpdateDestroyAPIView):
    """
    Класс API view, для endpoint'a просмотра, изменения и удаления конкретного рецепта.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    lookup_field = 'pk'  # По какому (уникальному) полю модели будет найден рецепт.
    lookup_url_kwarg = 'pk'  # Какой параметр указать в urlpatterns, для поиска рецепта.
    permission_classes = [IsOwnerOrReadOnly]


class RecipeListCreateGenericAPIView(GenericAPIView):
    """
    Класс API view, для endpoint'a просмотра перечня рецептов и создания новых.
    """
    queryset = Recipe.objects.all()  # Как и где достать наши объекты

    def get_serializer_class(self):
        """В зависимости от метода HTTP возвращает соответствующий класс для создания сериализатора"""
        if self.request.method == 'POST':
            return RecipeCreateSerializer
        return RecipeListSerializer

    def get(self, request, *args, **kwargs):
        """
        Метод `get` вызывается автоматический, когда HTTP метод запроса является `GET`.
        """
        queryset = self.get_queryset()
        serializer: ModelSerializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Метод `post` вызывается автоматический, когда HTTP метод запроса является `POST`.
        """
        serializer: ModelSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save(user=self.request.user)

        serializer = RecipeDetailSerializer(instance=recipe)
        return Response(serializer.data, status=201)


class DetailRecipeGenericAPIView(GenericAPIView):
    """
    Класс API view, для endpoint'a просмотра, изменения и удаления конкретного рецепта.
    """
    queryset = Recipe.objects.all()  # Как и где достать наш объект

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeDetailSerializer
        return RecipeCreateSerializer

    def get(self, request, pk: int, *args, **kwargs):
        recipe = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(instance=recipe)
        return Response(serializer.data)

    def put(self, request, pk: int, *args, **kwargs):
        recipe = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(data=request.data, instance=recipe)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk: int, *args, **kwargs):
        recipe = get_object_or_404(self.get_queryset(), pk=pk)

        # partial=True означает, что это частичное обновление, и не все поля могут быть переданы.
        serializer = self.get_serializer(data=request.data, instance=recipe, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk: int, *args, **kwargs):
        recipe = get_object_or_404(self.get_queryset(), pk=pk)
        recipe.delete()
        return Response(status=204)


@api_view()  # Это только для функций
def list_create_recipe_api_view(request):
    res = []
    for recipe in Recipe.objects.all():
        object_dict = {
            "id": recipe.id,
            "name": recipe.name,
            "preview_image": recipe.preview_image.url,
            "created_at": recipe.created_at,
            "time_minutes": recipe.time_minutes,
            "user": recipe.user.id,
            "ingredients": recipe.ingredients.all().values_list("name", flat=True),
            "category": recipe.category
        }
        res.append(object_dict)

    return Response(res)


@api_view()  # Это только для функций
def detail_recipe_api_view(request, pk: int):
    recipe = get_object_or_404(Recipe, id=pk)
    object_dict = {
        "id": recipe.id,
        "name": recipe.name,
        "description": recipe.description,
        "preview_image": recipe.preview_image.url,
        "created_at": recipe.created_at,
        "time_minutes": recipe.time_minutes,
        "user": recipe.user.id,
        "ingredients": recipe.ingredients.all().values_list("name", flat=True),
        "category": recipe.category
    }
    return Response(object_dict)


class UploadImageAPIView(GenericAPIView):
    serializer_class = ImageSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        image: InMemoryUploadedFile = serializer.validated_data["image"]
        with open(f"{settings.MEDIA_ROOT}/images/{image.name}", "bw") as image_file:
            image_file.write(image.read())
        return Response({"name": image.name, "url": "images/" + image.name})