import base64

from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework import status
from djoser import serializers as djoser_serializers

from foods.models import (
    Recipe, Tag,
    Ingredient, RecipeIngredient
)
from django.conf import settings


User = get_user_model()


class CustomUserCreateSerializer(djoser_serializers.UserCreateSerializer):
    class Meta(djoser_serializers.UserCreateSerializer.Meta):
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name', 'password'
        )


class UserRetrieveListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        if (self.context['request'].user.is_authenticated
            and obj.subscribing.filter(
                user=self.context['request'].user
        ).exists()):
            return True
        return False


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateIngredientAmountSerializer(
    serializers.ModelSerializer
):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=settings.CONSTANTS.get('MIN_TIME_BOUNDARY'),
        max_value=settings.CONSTANTS.get('MAX_TIME_BOUNDARY')
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True
    )
    tags = TagSerializer(many=True)
    author = UserRetrieveListSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name',
            'image', 'text', 'cooking_time'
        )

    def get_is_in_shopping_cart(self, obj):
        if (self.context['request'].user.is_authenticated
            and obj.shopping_list_recipes.filter(
                author=self.context['request'].user
        ).exists()):
            return True
        return False

    def get_is_favorited(self, obj):
        if (self.context['request'].user.is_authenticated
            and obj.favorite_recipes.filter(
                author=self.context['request'].user
        ).exists()):
            return True
        return False


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name',
            'image', 'cooking_time'
        )


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = CreateIngredientAmountSerializer(
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=settings.CONSTANTS.get('MIN_TIME_BOUNDARY'),
        max_value=settings.CONSTANTS.get('MAX_TIME_BOUNDARY')
    )

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

    def bulk_creating_recipe_ingredients(self, sentence, recipe) -> None:
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(
                    id=ingredient_data.get('id')
                ),
                amount=ingredient_data['amount']
            ) for ingredient_data in sentence
        ])

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        list_of_tags: list = []
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags_data:
            current_tag = get_object_or_404(Tag, id=tag.id)
            list_of_tags.append(current_tag)
        recipe.tags.set(list_of_tags)
        self.bulk_creating_recipe_ingredients(
            sentence=ingredients_data, recipe=recipe
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
        instance.recipe_ingredients.all().delete()
        self.bulk_creating_recipe_ingredients(
            sentence=ingredients_data, recipe=instance
        )
        instance.save()
        return instance

    def validate(self, data):
        tags = data.get('tags')
        if not tags or len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Tags should be unique and not empty!'
            )
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Ingredients list cant be empty!'
            )
        len_unit_in_ingredients: list[int] = [
            unit.get('id') for unit in ingredients
        ]
        if (len(len_unit_in_ingredients)
                != len(set(len_unit_in_ingredients))):
            raise serializers.ValidationError(
                'Ingredients should be unique!'
            )
        for ingredient_data in ingredients:
            try:
                Ingredient.objects.get(
                    id=ingredient_data.get('id')
                )
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    'Not existing ingredient'
                )
        return data


class FollowingSerializer(UserRetrieveListSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(UserRetrieveListSerializer.Meta):
        fields = (UserRetrieveListSerializer.Meta.fields
                  + ('recipes_count', 'recipes'))
        read_only_fields = ('email', 'username')

    def validate(self, data):
        author = self.instance
        user = self.context['request'].user
        if author.subscribing.filter(user=user).exists():
            raise serializers.ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise serializers.ValidationError(
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
