from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    BASE, VIP, PREMIUM = range(1, 4)
    SUB_TYPES = (
        (BASE, 'Base subscription'),
        (VIP, 'VIP subscription'),
        (PREMIUM, 'Premium subscription')
    )

    description = models.CharField(max_length=2000, null=True, blank=True)
    profile_pic = models.ImageField(upload_to='avatars', null=True)
    subscription = models.PositiveSmallIntegerField(choices=SUB_TYPES, default=BASE)
    matches = models.ManyToManyField('self', symmetrical=False)

    def get_swipes_count(self, sub_type):
        swipes_count = {self.BASE: 20, self.VIP: 100, self.PREMIUM: float('inf')}
        return swipes_count[sub_type]
