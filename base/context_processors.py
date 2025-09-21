from django.db.models import Q

from .models import HouseInvitation, House
from django.utils import timezone


def user_invitations(request):
    if request.user.is_authenticated:
        now = timezone.now()
        invitations = HouseInvitation.objects.filter(
            invited_user=request.user,
            accepted=False,
            expires_at__gt=now
        )
    else:
        invitations = []
    return {'user_invitations': invitations}


def user_houses(request):
    pk = request.resolver_match.kwargs.get("pk") if request.resolver_match else None

    if request.user.is_authenticated:
        qs = House.objects.filter(
            Q(owner=request.user) | Q(members=request.user)
        ).distinct()

        if pk:
            qs = qs.exclude(id=pk)

        houses = qs
    else:
        houses = []

    return {"houses": houses}
