from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Choices


User = get_user_model()


class Profile(models.Model):
    BASE, VIP, PREMIUM = range(1, 4)
    SUB_TYPES = (
        (BASE, 'Base subscription'),
        (VIP, 'VIP subscription'),
        (PREMIUM, 'Premium subscription')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=2000)
    profile_pic = models.ImageField(upload_to='avatars')
    subscription = models.PositiveSmallIntegerField(choices=SUB_TYPES, default=BASE)
    matches = models.ManyToManyField('self', null=True, blank=True)

    def get_swipes_count(self, sub_type):
        swipes_count = {self.BASE: 20, self.VIP: 100, self.PREMIUM: float('inf')}
        return swipes_count[sub_type]
