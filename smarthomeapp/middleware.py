from datetime import timedelta
from django.utils import timezone


class UpdateLastActiveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            now = timezone.now()
            if (
                    not request.user.last_seen or
                    now - request.user.last_seen > timedelta(minutes=1)
            ):
                request.user.last_seen = now
                request.user.save(update_fields=['last_seen'])

        return self.get_response(request)
