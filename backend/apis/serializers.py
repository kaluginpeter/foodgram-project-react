import base64

from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from rest_framework import serializers as rest_framework_serializers
from rest_framework import status
from djoser import serializers as djoser_serializers

from users.models import Follow
from foods.models import (
    Recipe, Tag,
    Ingredient, ShoppingList,
    Favorite, RecipeIngredient
)


User = get_user_model()


class CustomUserCreateSerializer(djoser_serializers.UserCreateSerializer):
    class Meta(djoser_serializers.UserCreateSerializer.Meta):
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name', 'password'
        )


class UserRetrieveListSerializer(rest_framework_serializers.ModelSerializer):
    is_subscribed = rest_framework_serializers.SerializerMethodField()
    first_name = rest_framework_serializers.CharField(required=False)
    last_name = rest_framework_serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        if self.context.get('request').user.is_authenticated \
            and Follow.objects.filter(
                user=self.context.get('request').user, author=obj
        ).exists():
            return True
        return False


class TagSerializer(rest_framework_serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(rest_framework_serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(rest_framework_serializers.ModelSerializer):
    id = rest_framework_serializers.ReadOnlyField(source='ingredient.id')
    name = rest_framework_serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = rest_framework_serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateIngredientAmountSerializer(
    rest_framework_serializers.ModelSerializer
):
    id = rest_framework_serializers.IntegerField()
    amount = rest_framework_serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class Base64ImageField(rest_framework_serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(rest_framework_serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True
    )
    tags = TagSerializer(many=True)
    author = UserRetrieveListSerializer()
    is_favorited = rest_framework_serializers.SerializerMethodField()
    is_in_shopping_cart = rest_framework_serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name',
            'image', 'text', 'cooking_time'
        )

    def get_is_in_shopping_cart(self, obj):
        if self.context.get('request').user.is_authenticated \
            and ShoppingList.objects.filter(
                author=self.context.get('request').user,
                recipe=obj
        ).exists():
            return True
        return False

    def get_is_favorited(self, obj):
        if self.context.get('request').user.is_authenticated \
            and Favorite.objects.filter(
                author=self.context.get('request').user,
                recipe=obj
        ).exists():
            return True
        return False


class RecipeShortSerializer(rest_framework_serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name',
            'image', 'cooking_time'
        )


class CreateRecipeSerializer(rest_framework_serializers.ModelSerializer):
    ingredients = CreateIngredientAmountSerializer(
        many=True
    )
    tags = rest_framework_serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "tags", "ingredients",
            "name", "image",
            "text", "cooking_time"
        )
        read_only_fields = ('author',)

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance, context={'request': self.context.get('request')}
        )
        return serializer.data

    def create(self, validated_data):
        validated_data['author'] = self.context.get('request').user
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        lst: list = list()
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags_data:
            current_tag = get_object_or_404(Tag, id=tag.id)
            lst.append(current_tag)
        recipe.tags.set(lst)
        for ingredient_data in ingredients_data:
            amount = ingredient_data.pop('amount')
            ingredient = Ingredient.objects.get(id=ingredient_data.get('id'))
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            instance.tags.set(tags_data)

        ingredients_data = validated_data.pop('ingredients')
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data.get('id'))
            RecipeIngredient.objects.create(
                recipe=instance, ingredient=ingredient,
                amount=ingredient_data.get('amount')
            )
        instance.save()
        return instance

    def validate(self, data):
        tags = data.get('tags')
        if not tags or len(tags) != len(set(tags)):
            raise rest_framework_serializers.ValidationError(
                'Tags should be unique and not empty!'
            )
        ingredients = data.get('ingredients')
        if not ingredients:
            raise rest_framework_serializers.ValidationError(
                'Ingredients list cant be empty!'
            )
        if (len([unit.get('id') for unit in ingredients])
                != len(set([unit.get('id') for unit in ingredients]))):
            raise rest_framework_serializers.ValidationError(
                'Ingredients should be unique!'
            )
        for ingredient_data in ingredients:
            try:
                Ingredient.objects.get(
                    id=ingredient_data.get('id')
                )
            except Ingredient.DoesNotExist:
                raise rest_framework_serializers.ValidationError(
                    'Not existing ingredient'
                )
            if ingredient_data.get('amount') < 1:
                raise rest_framework_serializers.ValidationError(
                    'Amount ingredient cant be less than zero!'
                )
        cooking_time = data.get('cooking_time')
        if cooking_time < 1:
            raise rest_framework_serializers.ValidationError(
                'Cooking time cant be less than 1 minute'
            )
        return data


class FollowingSerializer(UserRetrieveListSerializer):
    recipes_count = rest_framework_serializers.SerializerMethodField()
    recipes = rest_framework_serializers.SerializerMethodField()

    class Meta(UserRetrieveListSerializer.Meta):
        fields = UserRetrieveListSerializer.Meta.fields \
            + ('recipes_count', 'recipes')
        read_only_fields = ('email', 'username')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(user=user, author=author).exists():
            raise rest_framework_serializers.ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise rest_framework_serializers.ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data
