from django.contrib.auth.models import AbstractUser
from django.contrib.gis.geos import Point
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.gis.db import models


class User(AbstractUser):
    BASE, VIP, PREMIUM = range(1, 4)
    SUB_TYPES = (
        (BASE, 'Base subscription'),
        (VIP, 'VIP subscription'),
        (PREMIUM, 'Premium subscription')
    )
    SEX_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, null=True)
    age = models.PositiveSmallIntegerField(null=True, validators=[MinValueValidator(18), MaxValueValidator(150)])
    preferred_sex = models.CharField(max_length=1, choices=SEX_CHOICES, null=True)
    preferred_age_min = models.PositiveSmallIntegerField(default=18)
    preferred_age_max = models.PositiveSmallIntegerField(default=150)
    description = models.CharField(max_length=2000, null=True, blank=True)
    profile_pic = models.ImageField(upload_to='avatars', null=True)
    subscription = models.PositiveSmallIntegerField(choices=SUB_TYPES, default=BASE)
    relations = models.ManyToManyField('self', through='Relationship', symmetrical=False)
    location = models.OneToOneField('Location', null=True, on_delete=models.CASCADE)
    search_radius = models.PositiveSmallIntegerField(default=5)

    @property
    def homo(self):
        return self.preferred_sex == self.sex

    @property
    def opposite_sex(self):
        return 'M' if self.sex == 'F' else 'F'

    def get_swipes_count(self):
        swipes_count = {self.BASE: 20, self.VIP: 100, self.PREMIUM: float('inf')}
        return swipes_count[self.subscription]

    # def get_search_radius(self):
    #     radius = {self.BASE: 10, self.VIP: 25}
    #     return radius[self.subscription]
    #
    # def save(self, *args, **kwargs):
    #     self.get_search_radius()
    #     super().save(*args, **kwargs)


class Location(models.Model):
    last_location = models.PointField(default=Point(0, 0))
    last_modified = models.DateTimeField(auto_now=True)


class Relationship(models.Model):
    BLOCKED, LIKED = 1, 2
    REL_STATUSES = (
        (BLOCKED, 'Blocked'),
        (LIKED, 'Liked')
    )
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user')
    to_user = models.ForeignKey(User, models.CASCADE, related_name='to_user')
    status = models.PositiveSmallIntegerField(choices=REL_STATUSES)
