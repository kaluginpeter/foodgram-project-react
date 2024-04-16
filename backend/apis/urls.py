from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from users import views as users_views
from foods import views as foods_views

router = DefaultRouter()
router.register(
    'users', users_views.CustomRetrieveListUserViewSet, basename='users'
)
router.register('tags', foods_views.TagViewSet, basename='tags')
router.register(
    'ingredients', foods_views.IngredientViewSet, basename='ingredients'
)
router.register('recipes', foods_views.RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken'))
]
