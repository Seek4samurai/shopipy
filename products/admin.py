from django.db import models
from django.contrib import admin
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from .models import Category, Product, Brand, Brick, Collection


# Register your models here.
@admin.register(Brand)
@admin.register(Brick)
@admin.register(Collection)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


class PriceForm(ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def clean(self):
        stock_items = self.cleaned_data["stock_items"]

        # Constraints here
        if stock_items != [""]:
            for group in stock_items:
                quantity = 0
                total = stock_items[group]["total"]
                for item in stock_items[group]["items"]:
                    quantity += int(stock_items[group]["items"][item]["qty"])
                if quantity != int(stock_items[group]["total"]):
                    raise ValidationError(
                        f"Error: you've provided Item: \"{stock_items[group]['title']}\" with Total = \"{int(stock_items[group]['total'])}\", which doesn't matches with the item counts. Please check the items \"qty\" or update the \"total\" value."
                    )

        return self.cleaned_data


class ProductAdmin(admin.ModelAdmin):
    form = PriceForm
    fieldsets = (
        (None, {"fields": ("id",)}),
        (
            "Product Section",
            {
                "fields": (
                    "brand",
                    "title",
                    "category",
                    "brick",
                    "collection",
                    "gender",
                    "mrp",
                    "wsp",
                )
            },
        ),
        (
            "Image Section",
            {
                "fields": (
                    "image_1",
                    "image_2",
                    "image_3",
                    "image_4",
                )
            },
        ),
        (
            "Stock items",
            {
                "fields": (
                    "go_live_date",
                    "stock_items",
                    "is_active",
                )
            },
        ),
        (
            "Miscellaneous",
            {
                "fields": (
                    "style_code",
                    "style_2",
                    "style_region",
                    "uploaded_by",
                )
            },
        ),
    )
    list_display = [
        "id",
        "title",
        "brand",
        "category",
        "brick",
        "collection",
        "mrp",
        "is_active",
        "go_live_date",
    ]
    readonly_fields = [
        "id",
        "uploaded_by",
    ]

    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Product, ProductAdmin)
