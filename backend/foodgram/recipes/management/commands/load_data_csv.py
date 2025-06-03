from django.core.management.base import BaseCommand
import json
from recipes.models import Ingredient

class Command(BaseCommand):
    help = 'Import ingredients from JSON file'

    def handle(self, *args, **options):
        with open('/app/data/ingredients.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            count = 0
            for item in data:
                _, created = Ingredient.objects.get_or_create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
                if created:
                    count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Imported {count} ingredients')
