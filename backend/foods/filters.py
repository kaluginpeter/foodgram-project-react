import django_filters
from django_filters import rest_framework as filters
from django.contrib.postgres.search import SearchVector, TrigramSimilarity

from .models import Recipe, Tag, Ingredient


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='filter_name')

    class Meta:
        model = Ingredient
        fields = []

    def filter_name(self, queryset, name, value):
        if value:
            q = value.lower()
            vector = SearchVector('name')
            vector_trgm = TrigramSimilarity(
                'name', q, raw=True, fields=('name')
            )
            return queryset.annotate(
                search=vector
            ).order_by('name').filter(
                search=q
            ) or queryset.annotate(
                similarity=vector_trgm
            ).filter(similarity__gt=0.3).order_by('name')
        return queryset


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.NumberFilter(
        field_name='favorite_recipes', method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.NumberFilter(
        field_name='shopping_list_recipes',
        method='filter_is_in_shopping_cart'
    )

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value == 1:
                return queryset.filter(favorite_recipes__author=user)
            elif value == 0:
                return queryset.exclude(
                    favorite_recipes__author=user
                )
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value == 1:
                return queryset.filter(shopping_list_recipes__author=user)
            elif value == 0:
                return queryset.exclude(
                    shopping_list_recipes__author=user
                )
        return queryset
