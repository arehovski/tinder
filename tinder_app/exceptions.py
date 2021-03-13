from django.core.exceptions import PermissionDenied


class ParticipantsLimitException(PermissionDenied):
    pass
