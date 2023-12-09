from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomerUser, Orders
from rangefilter.filters import DateRangeQuickSelectListFilterBuilder

import csv
import pandas as pd


class CustomerUserAdmin(UserAdmin):
    model = CustomerUser
    list_display = (
        "email",
        "first_name",
        "last_name",
        "region",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "region", "cart")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "region",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    search_fields = ("email", "first_name", "last_name", "region")
    ordering = ("email",)


class OrderAdmin(admin.ModelAdmin):
    def download_selected_orders_to_excel_sheet(modeladmin, request, queryset):
        dataset = []
        for order in queryset:
            for field in order.items:
                field["username"] = order.name
                field["order_id"] = str(order.id)
                dataset.append(field)

        df = pd.DataFrame(dataset)
        df.to_excel("name.xlsx", index=False)

    fieldsets = (
        (None, {"fields": ("id", "delivered")}),
        (
            "Details",
            {
                "fields": (
                    "name",
                    "region",
                    "date",
                    "total_mrp",
                    "total_wsp",
                    "items",
                )
            },
        ),
    )
    list_display = [
        "id",
        "name",
        "region",
        "date",
        "delivered",
    ]
    readonly_fields = [
        "id",
    ]
    list_filter = (("date", DateRangeQuickSelectListFilterBuilder()),)
    actions = [download_selected_orders_to_excel_sheet]


# Register the custom user model admin
admin.site.register(CustomerUser, CustomerUserAdmin)
admin.site.register(Orders, OrderAdmin)
