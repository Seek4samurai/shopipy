import jwt
from django.conf import settings
from django.http import JsonResponse


class TokenAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        authorization_header = request.META.get("HTTP_AUTHORIZATION", None)
        if authorization_header:
            try:
                token_prefix, token = authorization_header.split()
                if token_prefix.lower() == "bearer":
                    try:
                        payload = jwt.decode(
                            token, settings.SECRET_KEY, algorithms=["HS256"]
                        )
                        # print("Decoded token", token, payload)
                        request.user_id = payload.get("user_id")
                    except jwt.ExpiredSignatureError:
                        print("Token expired")
                        return JsonResponse({"error": "Token expired"}, status=401)
                    except jwt.DecodeError:
                        print("Invalid token")
                        return JsonResponse({"error": "Invalid token"}, status=401)
                else:
                    print("Invalid token prefix")
                    return JsonResponse({"error": "Invalid token prefix"}, status=401)
            except ValueError:
                print("Invalid authorization format")
                return JsonResponse(
                    {"error": "Invalid authorization format"}, status=401
                )

        response = self.get_response(request)
        return response
