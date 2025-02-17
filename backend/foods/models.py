from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.core.exceptions import ValidationError


class Tag(models.Model):
    name = models.CharField(
        max_length=150, unique=True, verbose_name='Name of tag'
    )
    color = models.CharField(
        max_length=64, unique=True, verbose_name='Color of tag'
    )
    slug = models.SlugField(
        max_length=64, unique=True, verbose_name='Slug of tag'
    )

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        return f'{self.name} |-| {self.color} |-| {self.slug}'


class Ingredient(models.Model):
    name = models.CharField(max_length=256, verbose_name='Name of ingredient')
    measurement_unit = models.CharField(
        max_length=16, verbose_name='Measure of unit'
    )

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        return f'{self.name} |-| {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='recipes', verbose_name='Author of recipe',
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ingredients for recipe'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes', verbose_name='Tag for recipe'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Image for recipe'
    )
    name = models.CharField(
        max_length=200, verbose_name='Name for recipe'
    )
    text = models.TextField(
        max_length=2048, verbose_name='Description of recipe'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=settings.CONSTANTS.get('MIN_TIME_BOUNDARY'),
                message='Time of cooking cant be less than 1 minute'
            ),
            MaxValueValidator(
                limit_value=settings.CONSTANTS.get('MAX_TIME_BOUNDARY'),
                message='Time of cooking cant be more than 32 000 minutes'
            )
        ], verbose_name='Time of cooking recipe in minutes')

    class Meta:
        ordering = ['-id']

    def clean(self):
        tags = self.tags.all()
        tag_names = set()
        for tag in tags:
            if tag.name in tag_names:
                raise ValidationError("Recipe cannot have duplicate tags.")
            tag_names.add(tag.name)

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=settings.CONSTANTS.get('MIN_TIME_BOUNDARY'),
                message='Amount must be at least 1'
            ),
            MaxValueValidator(
                limit_value=settings.CONSTANTS.get('MAX_TIME_BOUNDARY'),
                message='Max amount size cant be \
                  more than 32 000 mesurement of unit!'
            )
        ]
    )

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        return f'{self.author} |-| {self.recipe} |-| {self.amount}'


class Favorite(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='favorite_owners', verbose_name='Owner of favorite list',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite_recipes', verbose_name='Recipe',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        return f'{self.author} |-| {self.recipe}'


class ShoppingList(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='shopping_list_owners',
        verbose_name='Owner of shopping list',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_list_recipes', verbose_name='Recipe',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        return f'{self.author} |-| {self.recipe}'
