from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.postgres.aggregates import ArrayAgg

from .forms import RecipeForm, IngredientForm
from .models import Recipe, Ingredient


def home(request: WSGIRequest):
    recipes_queryset = (
        Recipe.objects.all()
        .prefetch_related("ingredients")
        .annotate(
            # Создание массива уникальных имен тегов для каждой заметки
            ingredients_list=ArrayAgg('ingredients__name', distinct=True)
        )
        .values("id", "name", "time_minutes", "preview_image", "ingredients_list", "category")
    )

    search = request.GET.get("search")
    if search:
        recipes_queryset = recipes_queryset.filter(description__search=search)

    print(recipes_queryset.query)

    return render(request, 'home.html', {"recipes": recipes_queryset})


@login_required
def create_recipe(request: WSGIRequest):
    form = RecipeForm()

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)  # Файлы находятся отдельно!
        if form.is_valid():
            recipe: Recipe = form.save(commit=False)  # Не сохранять в базу рецепт, а вернуть его объект.
            recipe.user = request.user
            recipe.save()  # Сохраняем в базу объект.
            form.save_m2m()  # Сохраняем отношения many to many для ингредиентов и рецепта.

            return HttpResponseRedirect("/")

    return render(request, 'recipe-form.html', {'recipe_form': form, 'ingredient_form': IngredientForm()})


@login_required
def update_recipe(request: WSGIRequest, recipe_id: int):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.user != request.user:
        return HttpResponseForbidden("You do not have permission to edit this recipe")

    form = RecipeForm(instance=recipe)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)  # Файлы находятся отдельно!
        if form.is_valid():
            recipe: Recipe = form.save()
            return HttpResponseRedirect(reverse("show-recipe", args=(recipe.id,)))

    return render(request, 'recipe-form.html', {'form': form})


def show_recipe(request: WSGIRequest, recipe_id: int):
    recipe: Recipe = get_object_or_404(Recipe, id=recipe_id)
    return render(request, "recipe/recipe.html", {"recipe": recipe})


@login_required
def create_ingredient(request: WSGIRequest):
    form = IngredientForm()
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            ingredient: Ingredient = form.save(commit=False)
            ingredient.user = request.user
            ingredient.save()
            form.save_m2m()

            return HttpResponseRedirect("/recipe/create/")

    return render(request, 'recipe-form.html', {'recipe_form': RecipeForm, 'ingredient_form': form})
