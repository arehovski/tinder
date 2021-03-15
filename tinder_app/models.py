from django.contrib.auth.models import AbstractUser
from django.contrib.gis.geos import Point
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.gis.db import models
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from tinder_app.exceptions import ParticipantsLimitException


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

    def add_relation(self, to_user, status):
        relation, created = Relationship.objects.get_or_create(
            from_user=self,
            to_user=to_user,
            defaults={'status': status}
        )
        return relation, created

    def get_user_likes(self):
        return self._get_user_relations(Relationship.LIKED)

    def get_user_dislikes(self):
        return self._get_user_relations(Relationship.DISLIKED)

    def get_related_likes(self):
        return self._get_related(Relationship.LIKED)

    def get_related_dislikes(self):
        return self._get_related(Relationship.DISLIKED)

    def get_matched_list(self):
        return self.relations.filter(
            to_users__from_user=self,
            to_users__status=Relationship.LIKED,
            from_users__to_user=self,
            from_users__status=Relationship.LIKED,
        )

    def is_matched(self, other):
        return Relationship.objects.filter(
            from_user=self,
            to_user=other,
            status=Relationship.LIKED
        ).exists() and \
        Relationship.objects.filter(
            from_user=other,
            to_user=self,
            status=Relationship.LIKED
        ).exists()

    def get_chat_id(self, other):
        return Chat.objects.filter(
            participants=self.id
        ).intersection(Chat.objects.filter(
            participants=other.id)
        ).first()

    def _get_user_relations(self, status):
        return self.relations.filter(
            to_users__from_user=self,
            to_users__status=status
        )

    def _get_related(self, status):
        return self.relations.filter(
            from_users__to_user=self,
            from_users__status=status
        )


    # def get_swipes_count(self):
    #     swipes_count = {self.BASE: 20, self.VIP: 100, self.PREMIUM: float('inf')}
    #     return swipes_count[self.subscription]

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
    DISLIKED, LIKED = range(2)
    REL_STATUSES = (
        (DISLIKED, 'Disliked'),
        (LIKED, 'Liked'),
    )
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_users')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_users')
    status = models.PositiveSmallIntegerField(choices=REL_STATUSES)


@receiver(post_save, sender=Relationship)
def create_chat_instance(sender, instance, **kwargs):
    user1 = instance.from_user
    user2 = instance.to_user
    if user1.is_matched(user2):
        chat = Chat.objects.create()
        chat.participants.add(user1, user2)


class Chat(models.Model):
    participants = models.ManyToManyField(User)

    def get_latest_message(self):
        try:
            return self.message_set.latest('timestamp')
        except Message.DoesNotExist:
            return None


@receiver(m2m_changed, sender=Chat.participants.through)
def check_chat_participants(sender, instance, action='pre_add', **kwargs):
    if instance.participants.count() > 2:
        raise ParticipantsLimitException()


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='sender', null=True)
    text = models.CharField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('timestamp',)
