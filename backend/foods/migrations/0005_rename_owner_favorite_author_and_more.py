# Generated by Django 5.0.4 on 2024-04-13 12:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0004_remove_recipeingredient_only_one_ingredient_for_recipe'),
    ]

    operations = [
        migrations.RenameField(
            model_name='favorite',
            old_name='owner',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='shoppinglist',
            old_name='owner',
            new_name='author',
        ),
    ]
