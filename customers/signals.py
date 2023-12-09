# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth import get_user_model
# from .models import CustomerUser


# @receiver(post_save, sender=CustomerUser)
# def create_customer_user(sender, instance, created, **kwargs):
#     if created:
#         CustomerUser.objects.create(email=instance.email)
