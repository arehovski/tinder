import datetime

from django.contrib.gis.geos import Point
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
            if delta < datetime.timedelta(seconds=60):
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
        proposals = User.objects.filter(
            sex=user.sex if user.homo else user.opposite_sex,
            preferred_sex=user.sex,
            age__range=(user.preferred_age_min, user.preferred_age_max),
            preferred_age_min__lte=user.age,
            preferred_age_max__gte=user.age,
        ).exclude(
            username=user.username
        )
