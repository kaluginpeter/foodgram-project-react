from datetime import datetime as dt
from urllib.parse import unquote
from http import HTTPStatus
from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.db.models import Sum
from django.shortcuts import get_object_or_404

from apis import serializers as apis_serializers
from . import models as foods_models
from .filters import RecipeFilter, IngredientFilter
from .permissions import IsAuthorOrPersonal


class TagViewSet(ModelViewSet):
    queryset = foods_models.Tag.objects.all()
    serializer_class = apis_serializers.TagSerializer
    pagination_class = None
    http_method_names = ['get']
    lookup_field = 'id'


class IngredientViewSet(ModelViewSet):
    serializer_class = apis_serializers.IngredientSerializer
    pagination_class = None
    http_method_names = ['get']
    lookup_field = 'id'
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = IngredientFilter
    search_fields = ['^name', 'name']

    def get_queryset(self):
        queryset = foods_models.Ingredient.objects.all()
        query = self.request.GET.get('name')
        if query:
            q = query.lower()
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


class RecipeViewSet(ModelViewSet):
    queryset = foods_models.Recipe.objects.all()
    lookup_field = 'id'
    permission_classes = (IsAuthorOrPersonal,)
    http_method_names = ['get', 'post', 'delete', 'patch']
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == permissions.SAFE_METHODS:
            return apis_serializers.RecipeSerializer
        return apis_serializers.CreateRecipeSerializer

    @action(
        detail=True,
        lookup_field='id',
        methods=['post', 'delete'],
        permission_classes=[IsAuthorOrPersonal]
    )
    def favorite(self, request, id):
        if request.method == 'POST':
            try:
                recipe = foods_models.Recipe.objects.get(id=id)
            except foods_models.Recipe.DoesNotExist:
                return Response(
                    data={'errors': 'Not existing recipe'},
                    status=HTTPStatus.BAD_REQUEST
                )
            if foods_models.Favorite.objects.filter(
                author=request.user, recipe__id=id
            ).exists():
                return Response(
                    data={'errors': 'Recipe has already added!'},
                    status=HTTPStatus.BAD_REQUEST
                )
            foods_models.Favorite.objects.create(
                author=request.user, recipe=recipe
            )
            serializer = apis_serializers.RecipeShortSerializer(recipe)
            return Response(serializer.data, status=HTTPStatus.CREATED)
        else:
            try:
                recipe = foods_models.Recipe.objects.get(id=id)
            except foods_models.Recipe.DoesNotExist:
                return Response(
                    data={'errors': 'Not existing recipe'},
                    status=HTTPStatus.NOT_FOUND
                )
            instc = foods_models.Favorite.objects.filter(
                author=request.user, recipe__id=id
            )
            if instc.exists():
                instc.delete()
                return Response(status=HTTPStatus.NO_CONTENT)
            return Response(
                data={'errors': 'Recipe has already deleted!'},
                status=HTTPStatus.BAD_REQUEST
            )

    @action(
        detail=True,
        lookup_field='id',
        methods=['post', 'delete'],
        permission_classes=[IsAuthorOrPersonal]
    )
    def shopping_cart(self, request, id):
        if request.method == 'POST':
            try:
                recipe = foods_models.Recipe.objects.get(id=id)
            except foods_models.Recipe.DoesNotExist:
                return Response(
                    data={'errors': 'Not existing recipe'},
                    status=HTTPStatus.BAD_REQUEST
                )
            if foods_models.ShoppingList.objects.filter(
                author=request.user, recipe__id=id
            ).exists():
                return Response(
                    data={'errors': 'Recipe has already added!'},
                    status=HTTPStatus.BAD_REQUEST
                )
            foods_models.ShoppingList.objects.create(
                author=request.user, recipe=recipe
            )
            serializer = apis_serializers.RecipeShortSerializer(recipe)
            return Response(serializer.data, status=HTTPStatus.CREATED)
        else:
            try:
                recipe = foods_models.Recipe.objects.get(id=id)
            except foods_models.Recipe.DoesNotExist:
                return Response(
                    data={'errors': 'Not existing recipe'},
                    status=HTTPStatus.NOT_FOUND
                )
            instc = foods_models.ShoppingList.objects.filter(
                author=request.user, recipe__id=id
            )
            if instc.exists():
                instc.delete()
                return Response(status=HTTPStatus.NO_CONTENT)
            return Response(
                data={'errors': 'Recipe has already deleted!'},
                status=HTTPStatus.BAD_REQUEST
            )

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_list_owners.exists():
            return Response(status=HTTPStatus.BAD_REQUEST)
        ingredients = foods_models.RecipeIngredient.objects.filter(
            recipe__shopping_list_recipes__author=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            amount=Sum('amount')
        )
        today = dt.today()
        shopping_list = (
            f'Date: {today:%Y-%m-%d}\n\n'
        )
        shopping_list += '\n'.join([
            f'| {unit.get("ingredient__name")} '
            f'| ({unit.get("ingredient__measurement_unit")}) '
            f'| {unit.get("amount")}'
            for unit in ingredients
        ])
        shopping_list += f'\n\nFoodgram Inc Corporation ({today:%Y})'
        shopping_list += '\n\nAll terms served'
        filename: str = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
