from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

import re
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from datetime import datetime

from customers.models import CustomerUser
from .models import Product
from .middleware import TokenAuthenticationMiddleware


# Create your views here.
class FetchProducts(APIView):
    def get(self, request):
        try:
            user_id = getattr(request, "user_id", None)
            active_user = CustomerUser.objects.get(email=user_id)
            active_user_region_string = active_user.region
            active_regions = ""

            if active_user_region_string:
                active_regions = active_user_region_string.split(",")

            product_fields = [field.name for field in Product._meta.get_fields()]
            products_list = []  # Create a list to store products for all regions

            product_fields.append("brand__name")
            product_fields.append("brick__name")
            product_fields.append("category__name")
            product_fields.append("collection__name")
            product_fields.append("uploaded_by__username")

            if not active_regions:
                print("Empty Regions")
                products = Product.objects.all().values(*product_fields)
                products_list.extend(products)

            else:
                print("Non-Empty Regions")
                for region in active_regions:
                    products = Product.objects.filter(
                        style_region__icontains=region.strip()
                    ).values(*product_fields)
                    products_list.extend(products)

            return Response(products_list, status=status.HTTP_200_OK)

        except Product.DoesNotExist:
            print("Object not found.")
            return Response(
                {"error": "Error occured"}, status=status.HTTP_404_NOT_FOUND
            )

        except CustomerUser.DoesNotExist:
            print("Object not found.")
            return Response(
                {"error": "Error occured"}, status=status.HTTP_404_NOT_FOUND
            )


# For unAuthenticated Users
class UnAuthFetchProducts(APIView):
    def get(self, request):
        product_fields = [field.name for field in Product._meta.get_fields()]

        product_fields.append("brand__name")
        product_fields.append("brick__name")
        product_fields.append("category__name")
        product_fields.append("collection__name")
        product_fields.append("uploaded_by__username")

        products = Product.objects.all().values(*product_fields)

        paginator_instance = Paginator(products, 5)
        page_number = request.GET.get("page")
        page_obj = paginator_instance.get_page(page_number)

        return Response(list(page_obj), safe=False, status=status.HTTP_200_OK)


class FetchItem(APIView):
    def get(self, request, id):
        try:
            obj = Product.objects.get(id=id)
            product_fields = [field.name for field in Product._meta.get_fields()]

            data = {}
            for field in product_fields:
                value = getattr(obj, field)
                if field == "uploaded_by":
                    data[field] = value.username if value else None
                elif hasattr(value, "name"):
                    data[field] = value.name
                else:
                    data[field] = value

            return JsonResponse(data)

        except Product.DoesNotExist:
            print("Object not found.")
            return Response(
                {"error": "Product not found!"}, status=status.HTTP_404_NOT_FOUND
            )


def filter_products(requests, item_type, category, gender, sort_by):
    filters = {
        "brick": item_type,
        "category": category,
        "gender": gender,
    }
    filters = {key: value for key, value in filters.items() if value != "Any"}

    filtered_products = Product.objects.all()

    # Apply filters dynamically to the queryset
    for field, value in filters.items():
        if field == "gender":
            all_values = value.split(",")
            q_object = Q()

            for val in all_values:
                val = val.strip()
                escaped_value = re.escape(val)
                regex_pattern = rf"\b{escaped_value}\b"
                q_object |= Q(gender__regex=regex_pattern)

            filtered_products = filtered_products.filter(q_object)

        else:
            all_values = value.split(",")
            q_object = Q()

            for val in all_values:
                val = val.strip()
                q_object |= Q(**{f"{field}__name": val})

            filtered_products = filtered_products.filter(q_object)

    products_data = list(filtered_products.values())

    # Sorting part if it exists
    if sort_by != "Any" and sort_by != "newest":
        sort_order = {"mrp_low_to_high": False, "mrp_high_to_low": True}
        sorting_param = sort_order.get(sort_by, False)

        products_data = sorted(
            products_data, key=lambda x: x["mrp"], reverse=sorting_param
        )
    elif sort_by == "newest":
        products_data = sorted(products_data, key=lambda x: x["created"], reverse=True)

    return JsonResponse(list(products_data), safe=False)
