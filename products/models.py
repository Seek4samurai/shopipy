from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from django.db import models
from io import BytesIO
from skimage.io import imsave
from skimage.transform import resize
from PIL import Image

import numpy as np
import uuid


# Create your models here.
class Brand(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "brands"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Brick(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "bricks"

    def __str__(self):
        return self.name


class Collection(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "collections"

    def __str__(self):
        return self.name


# Don't remove
def default_stock_items():
    return [""]


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey(
        Brand, related_name="brand", on_delete=models.SET_NULL, blank=False, null=True
    )
    title = models.CharField(max_length=255, blank=False, unique=True)
    category = models.ForeignKey(
        Category,
        related_name="category",
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
    )
    brick = models.ForeignKey(
        Brick, related_name="brick", on_delete=models.SET_NULL, blank=False, null=True
    )
    collection = models.ForeignKey(
        Collection,
        related_name="collection",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    gender = models.CharField(
        max_length=150,
        blank=False,
        help_text="Enter comma-separated values for genders (e.g., Men, Women, Kids)",
    )
    mrp = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    wsp = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    style_code = models.CharField(max_length=255, blank=True, null=True)  # future value
    style_2 = models.CharField(max_length=255, blank=True, null=True)
    image_1 = models.FileField(
        upload_to="media/",
        blank=True,
        null=True,
        help_text="Upload a valid portrait image",
    )
    image_2 = models.FileField(upload_to="media/", blank=True, null=True)
    image_3 = models.FileField(upload_to="media/", blank=True, null=True)
    image_4 = models.FileField(upload_to="media/", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    uploaded_by = models.ForeignKey(
        User,
        related_name="uploader",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
    )
    go_live_date = models.DateTimeField(
        blank=False, help_text="Date after which they can be booked"
    )
    style_region = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Enter comma-separated values (e.g., Western, South_Indian, North_Indian)",
    )
    stock_items = models.JSONField(
        default=default_stock_items,
        blank=False,
        help_text="Refer to documentation & jsonformatter.org.",
    )
    is_active = models.BooleanField(
        default=False, help_text="Products go live only if they're active"
    )

    class Meta:
        verbose_name_plural = "Products"
        ordering = ("-created",)

    def get_choices_as_list(self, field_name):
        field_value = getattr(self, field_name)
        if field_value:
            return [
                (choice.strip(), choice.strip()) for choice in field_value.split(",")
            ]
        return []

    def save(self, *args, **kwargs):
        uploaded_image = Image.open(self.image_1)
        image_array = np.array(uploaded_image)

        # new size of the image
        compressed_image = resize(image_array, (1920, 1280))

        compressed_pil_image = Image.fromarray(
            (compressed_image * 255).astype(np.uint8)
        )
        image_buffer = BytesIO()
        compressed_pil_image.save(image_buffer, format="JPEG")

        self.image_1.save(
            f"{self.image_1.name}",  # Preserve the original file name
            ContentFile(image_buffer.getvalue()),
            save=False,
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


@receiver(pre_save, sender=Product)
def add_uuid_to_stock_items(sender, instance, **kwargs):
    if instance.stock_items and instance.stock_items != [""]:
        for key, value in instance.stock_items.items():
            if "id" not in value:
                value["id"] = str(uuid.uuid4())


pre_save.connect(add_uuid_to_stock_items, sender=Product)
