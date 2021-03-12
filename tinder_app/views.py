import datetime
from itertools import chain

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db.models import F
from django.db.models.functions import Least
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from rest_framework import views
from rest_framework import status

from .models import User, Location
from .serializers import (
    UserRegisterSerializer,
    UserUpdateSerializer,
    UserChangePasswordSerializer,
    ProposalsListSerializer
)


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (AllowAny,)


class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserChangePasswordSerializer
    permission_classes = (IsAuthenticated,)


class UpdateUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = (IsAuthenticated,)


class CurrentUserLocationView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        longitude = float(request.POST.get('longitude'))
        latitude = float(request.POST.get('latitude'))
        if user.location:
            modified = user.location.last_modified
            delta = datetime.datetime.now(tz=modified.tzinfo) - modified
            if delta < datetime.timedelta(seconds=7200):
                return Response(
                    {'detail': 'Location can be changed every two hours.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            else:
                user.location.last_location = Point(longitude, latitude, srid=4326)
                user.location.save()
        else:
            location = Location.objects.create(
                last_location=Point(
                    longitude, latitude, srid=4326
                )
            )
            user.location = location
            user.save()
        return Response(
            {'detail': 'Location changed'}, status=status.HTTP_204_NO_CONTENT
        )


class ProposalsListView(generics.ListAPIView):
    serializer_class = ProposalsListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.get_serializer_context()['request'].user
        current_user_location = user.location.last_location
        user_likes = user.get_user_likes().values_list('id', flat=True)
        user_dislikes = user.get_user_dislikes().values_list('id', flat=True)
        related_dislikes = user.get_related_dislikes().values_list('id', flat=True)
        ids_to_exclude = set(chain(user_likes, user_dislikes, related_dislikes, [user.id]))

        proposals = User.objects.filter(
            sex=user.sex if user.homo else user.opposite_sex,
            preferred_sex=user.sex,
            age__range=(user.preferred_age_min, user.preferred_age_max),
            preferred_age_min__lte=user.age,
            preferred_age_max__gte=user.age,
        ).exclude(id__in=ids_to_exclude)

        proposals = proposals.annotate(
            radius=Least(user.search_radius, F('search_radius')),
            distance=Distance('location__last_location', current_user_location)
        ).filter(distance__lte=F('radius') * 1000).order_by('distance')

        return proposals


class SwipeView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        user = request.user
        to_user = get_object_or_404(User.objects.all(), id=pk)
        liked = request.POST.get('liked')
        relation, created = user.add_relation(to_user=to_user, status=int(liked))
        return Response({'detail': 'Relation created'}, status=status.HTTP_201_CREATED) if created \
            else Response({'detail': 'Relation already exists'}, status=status.HTTP_204_NO_CONTENT)

