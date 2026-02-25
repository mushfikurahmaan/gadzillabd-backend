from django.http import JsonResponse
from django.conf import settings


def verify_admin_path(request):
    guess = request.GET.get('path', '').strip().strip('/')
    actual = settings.ADMIN_URL_PATH.strip().strip('/')
    return JsonResponse({'match': guess == actual})
