from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token


# Create your views here.
def home(request):
    if request.method == "GET":
        return HttpResponse("Status Check!")
    else:
        return HttpResponse("This API only accepts GET requests.")


def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({"csrfToken": csrf_token})
