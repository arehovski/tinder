import random

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from faker import Faker

from tinder_app.models import User, Location


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        count = options['count']

        lat_min = 53.85
        lat_max = 53.94
        lng_min = 27.44
        lng_max = 27.64

        fake = Faker()

        sexual_orientation_list = random.choices(
            population=['hetero', 'homo'], weights=[0.9, 0.1], k=count)

        for i in range(count):
            lat = random.uniform(lat_min, lat_max)
            lng = random.uniform(lng_min, lng_max)
            user_age = random.randrange(18, 55)
            user_delta_plus = random.choice([1, 2, 3, 5, 8, 13])
            user_delta_minus = random.choice([1, 2, 3, 5, 8, 13])
            orientation = sexual_orientation_list[i]
            sex = random.choice(('M', 'F'))

            if orientation == 'homo':
                user_preferred_sex = sex
            else:
                user_preferred_sex = 'F' if sex == 'M' else 'M'

            location = Location.objects.create(last_location=Point(lng, lat))

            User.objects.create(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                subscription=random.choice((1, 2, 3)),
                age=user_age,
                sex=sex,
                preferred_sex=user_preferred_sex,
                preferred_age_min=(user_age-user_delta_minus),
                preferred_age_max=(user_age+user_delta_plus),
                location=location,
                search_radius=random.choice((10, 25))
            )
