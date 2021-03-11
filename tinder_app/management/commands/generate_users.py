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
            longitude = random.uniform(lng_min, lng_max)
            latitude = random.uniform(lat_min, lat_max)
            age = random.randrange(18, 55)
            age_delta = random.choice([2, 3, 5, 7, 10])
            orientation = sexual_orientation_list[i]
            sex = random.choice(('M', 'F'))
            first_name, last_name = fake.unique.name_male().split() if sex == 'M' else \
                fake.unique.name_female().split()

            if orientation == 'homo':
                user_preferred_sex = sex
            else:
                user_preferred_sex = 'F' if sex == 'M' else 'M'

            location = Location.objects.create(last_location=Point(longitude, latitude, srid=4326))

            User.objects.create(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                first_name=first_name,
                last_name=last_name,
                subscription=random.choice((1, 2, 3)),
                age=age,
                sex=sex,
                preferred_sex=user_preferred_sex,
                preferred_age_min=(age - age_delta),
                preferred_age_max=(age + age_delta),
                location=location,
                search_radius=random.choice((2, 5, 7, 10, 25))
            )
