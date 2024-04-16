import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()

import csv
from django.core.management.base import BaseCommand
from django.conf import settings

from foods.models import Ingredient


class Command(BaseCommand):
    help = 'Parse and import CSV data'

    def handle(self, *args, **kwargs):
        csv_file_path = os.path.join(
            settings.BASE_DIR, 'data/ingredients.csv'
        )
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                name, measurement_unit = row
                ingredient = Ingredient(
                    name=name,
                    measurement_unit=measurement_unit,
                )
                ingredient.save()
        self.stdout.write(self.style.SUCCESS('CSV data imported successfully'))
