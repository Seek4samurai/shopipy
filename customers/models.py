from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

import uuid


class CustomerUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomerUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    region = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Enter comma-separated values with underscore (e.g., Western, South_Indian, North_Indian)",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    cart = models.JSONField(
        blank=True,
        null=True,
        default=list,
        help_text="Refer to jsonformatter.org",
    )

    objects = CustomerUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customer_users",
        blank=True,
        verbose_name="groups",
        help_text="Groups this user belongs to. A user will get all permissions granted to each of their groups.",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customer_users_permissions",
        blank=True,
        verbose_name="user permissions",
        help_text="Specific permissions for this user.",
    )

    objects = CustomerUserManager()


# Don't remove
def default_stock_items():
    return [""]


class Orders(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delivered = models.BooleanField(default=False)
    name = models.CharField(max_length=200, db_index=True)
    region = models.CharField(max_length=150, blank=True, null=True)
    date = models.DateTimeField(blank=False)
    total_mrp = models.DecimalField(
        max_digits=9, decimal_places=2, blank=True, null=True
    )
    total_wsp = models.DecimalField(
        max_digits=9, decimal_places=2, blank=True, null=True
    )
    items = models.JSONField(
        default=default_stock_items,
        blank=False,
        help_text="Refer to documentation & jsonformatter.org.",
    )

    class Meta:
        verbose_name_plural = "Orders"

    def __str__(self):
        return self.name
