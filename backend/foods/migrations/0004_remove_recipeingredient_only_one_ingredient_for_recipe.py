# Generated by Django 5.0.4 on 2024-04-10 16:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0003_recipeingredient_only_one_ingredient_for_recipe'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='recipeingredient',
            name='only_one_ingredient_for_recipe',
        ),
    ]