from django.contrib import admin
from django.contrib.admin import display

from . import models as foods_models


@admin.register(foods_models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'author', 'added_in_favorites')
    readonly_fields = ('added_in_favorites',)
    list_filter = ('author', 'name', 'tags',)

    @display(description='Count recipes in favorites')
    def added_in_favorites(self, obj) -> int:
        return obj.favorite_recipes.count()


@admin.register(foods_models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


@admin.register(foods_models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


@admin.register(foods_models.ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe',)


@admin.register(foods_models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe',)


@admin.register(foods_models.RecipeIngredient)
class RecipeIngredient(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)
