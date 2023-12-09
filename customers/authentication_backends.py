from django.contrib.auth.backends import ModelBackend
from customers.models import CustomerUser


class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = CustomerUser.objects.get(email=email)
            if user.check_password(password):
                return user
        except CustomerUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomerUser.objects.get(pk=user_id)
        except CustomerUser.DoesNotExist:
            return None
