from django import forms
from .models import CustomerUser


class CustomerUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomerUser
        fields = ("first_name", "last_name", "email")
