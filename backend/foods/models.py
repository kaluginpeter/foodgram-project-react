from django.db import models
from django.core.validators import MinValueValidator
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

    def __str__(self) -> str:
        return f'{self.name} |-| {self.color} |-| {self.slug}'


class Ingredient(models.Model):
    name = models.CharField(max_length=256, verbose_name='Name of ingredient')
    measurement_unit = models.CharField(
        max_length=16, verbose_name='Measure of unit'
    )

    def __str__(self) -> str:
        return f'{self.name} |-| {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=False,
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
        Tag, blank=False,
        related_name='recipes', verbose_name='Tag for recipe'
    )
    image = models.ImageField(
        upload_to='recipes/images/', blank=False,
        verbose_name='Image for recipe'
    )
    name = models.CharField(
        max_length=200, blank=False, verbose_name='Name for recipe'
    )
    text = models.TextField(
        max_length=2048, blank=False, verbose_name='Description of recipe'
    )
    cooking_time = models.PositiveSmallIntegerField(
        blank=False, validators=[
            MinValueValidator(
                limit_value=1,
                message='Time of cooking cant be less than 1 minute'
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
        blank=False, validators=[
            MinValueValidator(
                limit_value=1,
                message='Amount must be at least 1'
            )
        ]
    )

    def __str__(self) -> str:
        return f'{self.author} |-| {self.recipe} |-| {self.amount}'


class Favorite(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=False,
        related_name='favorite_owners', verbose_name='Owner of favorite list',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, blank=False,
        related_name='favorite_recipes', verbose_name='Recipe',
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f'{self.author} |-| {self.recipe}'


class ShoppingList(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=False,
        related_name='shopping_list_owners',
        verbose_name='Owner of shopping list',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, blank=False,
        related_name='shopping_list_recipes', verbose_name='Recipe',
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f'{self.author} |-| {self.recipe}'
