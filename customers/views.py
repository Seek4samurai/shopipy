from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model, login, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from products.models import Product
from .models import Orders
from .forms import CustomerUser, CustomerUserCreationForm
from .middleware import TokenAuthenticationMiddleware
from . import serializers

import json
import jwt


class SignupView(APIView):
    def post(self, request):
        serializer = serializers.SignupSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Set expiration time for the access token (e.g., 1 hour)
            access_token_expiry = datetime.utcnow() + timedelta(hours=1)
            refresh_token_expiry = datetime.utcnow() + timedelta(hours=24)

            # Generate access token
            access_token = jwt.encode(
                {"user_id": str(user), "exp": access_token_expiry},
                settings.SECRET_KEY,  # key here
                algorithm="HS256",
            )
            # Generate refresh token
            refresh_token = jwt.encode(
                {"user_id": str(user), "exp": refresh_token_expiry},
                settings.SECRET_KEY_2,  # key here
                algorithm="HS256",
            )

            login(
                request,
                user,
                backend="customers.authentication_backends.EmailBackend",
            )

            return Response(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "message": "User registered and logged in successfully",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid form data"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginView(APIView):
    def post(self, request):
        serializer = serializers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        user = authenticate(
            request,
            email=email,
            password=password,
            backend="customers.authentication_backends.EmailBackend",
        )

        # Set expiration time for the access token (e.g., 1 hour)
        access_token_expiry = datetime.utcnow() + timedelta(hours=1)
        refresh_token_expiry = datetime.utcnow() + timedelta(hours=24)

        if user is not None:
            access_token = jwt.encode(
                {"user_id": str(user), "exp": access_token_expiry},
                settings.SECRET_KEY,  # key
                algorithm="HS256",
            )
            refresh_token = jwt.encode(
                {"user_id": str(user), "exp": refresh_token_expiry},
                settings.SECRET_KEY_2,  # key
                algorithm="HS256",
            )

            login(request, user)

            return Response(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "message": "User logged in successfully",
                },
                status=status.HTTP_200_OK,
            )

        else:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)


def validate_refresh_token(refresh_token):
    try:
        decoded_token = jwt.decode(
            refresh_token, settings.SECRET_KEY_2, algorithms=["HS256"]
        )
        # Check if the refresh token is expired
        expiration_timestamp = decoded_token.get("exp")
        if expiration_timestamp and timezone.now().timestamp() <= expiration_timestamp:
            return True
        else:
            return False
    except jwt.ExpiredSignatureError:
        print("Refresh token expired signature")
        return False
    except jwt.DecodeError:
        print("Refresh token decode error")
        return False


def generate_access_token(user):
    # Set expiration time for the access token (e.g., 1 hour)
    access_token_expiry = datetime.utcnow() + timedelta(hours=1)
    payload = {
        "user_id": str(user),
        "exp": access_token_expiry,
    }

    access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return access_token


@csrf_exempt
def refresh_token_view(request):
    if request.method == "POST":
        refresh_token = request.POST.get("refresh_token")

        if validate_refresh_token(refresh_token):
            decoded_token = jwt.decode(
                refresh_token, settings.SECRET_KEY_2, algorithms=["HS256"]
            )
            user = decoded_token["user_id"]
            new_access_token = generate_access_token(user)
            return JsonResponse({"access_token": new_access_token})
        else:
            return JsonResponse({"error": "Invalid refresh token"}, status=400)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def logout_view(request):
    if request.method == "POST":
        response = JsonResponse({"message": "Logout successful"})
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def save_cart_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        stock_id = data.get("stock_id")
        item_id = data.get("post_id")
        volume = data.get("volume")
        user_id = getattr(request, "user_id", None)

        try:
            json_data = {"stock_id": stock_id, "item_id": item_id, "volume": volume}
            active_user = CustomerUser.objects.get(email=user_id)
            userdata_fields = [field.name for field in CustomerUser._meta.get_fields()]
            cart_data = active_user.cart

            # Checking if cart_data is None, if so initialize it with an empty list
            if cart_data is None:
                cart_data = []

            for item in cart_data:
                if item["stock_id"] == stock_id:
                    return JsonResponse({"Message": "Item already in cart"}, status=200)

            cart_data.append(json_data)
            active_user.cart = cart_data
            active_user.save()

        except CustomerUser.DoesNotExist:
            print("Object not found.")

        return JsonResponse({"Message": "Item added"}, status=200)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


def fetch_cart(request):
    if request.method == "GET":
        user_id = getattr(request, "user_id", None)
        try:
            active_user = CustomerUser.objects.get(email=user_id)
            cart_data = active_user.cart
            return JsonResponse({"cart_data": cart_data}, status=200)

        except CustomerUser.DoesNotExist:
            print("Object not found.")
            return JsonResponse({"error": "Error occured"}, status=500)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


def fetch_cart_data(request):
    if request.method == "GET":
        user_id = getattr(request, "user_id", None)
        product_fields = [field.name for field in Product._meta.get_fields()]
        cart_data = []
        stock_data = []
        try:
            active_user = CustomerUser.objects.get(email=user_id)
            cart_items = active_user.cart
            for item in cart_items:
                try:
                    obj = Product.objects.get(id=item["item_id"])
                    data = {}
                    for field in product_fields:
                        value = getattr(obj, field)
                        if field == "uploaded_by":
                            data[field] = value.username if value else None
                        elif field == "stock_items":
                            for i in value:
                                if value[i]["id"] == item["stock_id"]:
                                    data[field] = value[i]
                        elif hasattr(value, "name"):
                            data[field] = value.name
                        else:
                            data[field] = value

                    cart_data.append(data)

                except Product.DoesNotExist:
                    return JsonResponse({"error": "Product not found."}, status=500)

            return JsonResponse({"cart_data": cart_data}, status=200)

        except CustomerUser.DoesNotExist:
            print("Object not found.")
            return JsonResponse({"error": "Error occured"}, status=500)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def update_cart_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        stock_id = data.get("stock_id")
        user_id = getattr(request, "user_id", None)
        try:
            active_user = CustomerUser.objects.get(email=user_id)
            cart_data = active_user.cart

            updated_cart_data = [
                item for item in cart_data if item["stock_id"] != stock_id
            ]
            active_user.cart = updated_cart_data
            active_user.save()

            return JsonResponse({"cart_data": updated_cart_data}, status=200)

        except CustomerUser.DoesNotExist:
            print("Object not found.")
            return JsonResponse({"error": "Error occured"}, status=500)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)  # Convert Decimal to string
        if isinstance(obj, UUID):
            return str(obj)  # Convert UUID to string
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")  # Convert datetime to string
        return super().default(obj)


def place_order(request):
    if request.method == "GET":
        user_id = getattr(request, "user_id", None)
        product_fields = [field.name for field in Product._meta.get_fields()]
        item_list = []
        try:
            active_user = CustomerUser.objects.get(email=user_id)
            active_cart_data = active_user.cart
            for item in active_cart_data:
                item_id = item["item_id"]
                try:
                    obj = Product.objects.get(id=item_id)
                    data = {}
                    for field in product_fields:
                        value = getattr(obj, field)
                        if field == "uploaded_by":
                            data[field] = value.username if value else None
                        elif field == "stock_items":
                            for i in value:
                                if value[i]["id"] == item["stock_id"]:
                                    data["total_items"] = value[i]["total"]
                                    data["stock_title"] = value[i]["title"]
                                    data["stock_id"] = str(value[i]["id"])
                                    data["discount"] = value[i]["discount"]
                                    data["items"] = value[i]["items"]
                                    if value[i]["total"]:
                                        if int(value[i]["total"]) < item["volume"]:
                                            return JsonResponse(
                                                {
                                                    "error": f"{value[i]['title']} is Out Of Stock."
                                                },
                                                status=500,
                                            )
                                        else:
                                            data["volume"] = item["volume"]

                        elif hasattr(value, "name"):
                            data[field] = value.name
                        else:
                            if (
                                type(value) == UUID
                                or type(value) == Decimal
                                or type(value) == datetime
                            ):
                                if field == "id":
                                    data["product_id"] = str(value)
                                else:
                                    data[field] = str(value)
                            else:
                                data[field] = value
                    item_list.append(data)

                except Product.DoesNotExist:
                    return JsonResponse({"error": "Product not found."}, status=500)

            name = active_user.email
            region = active_user.region
            date = timezone.now()
            items = item_list

            # another approach to jsonfield but with "\n" & "\"
            # items = json.dumps(item_list, cls=JsonEncoder, indent=4)

            order = Orders(name=name, region=region, date=date, items=items)
            order.save()

            # clearing cart after placing order
            active_user.cart = active_user.cart.clear()
            active_user.save()

            return HttpResponse(status=200)

        except CustomerUser.DoesNotExist:
            print("Object not found.")
            return JsonResponse({"error": "Error occured"}, status=500)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
