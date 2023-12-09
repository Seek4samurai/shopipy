from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.login_view, name="login_customer"),
    path("refresh-token/", views.refresh_token_view, name="refresh_token"),
    path("signup/", views.signup_view, name="signup_customer"),
    path("logout/", views.logout_view, name="logout"),
    path("cart/", views.fetch_cart, name="fetch_cart"),
    path("cart_data/", views.fetch_cart_data, name="fetch_cart_data"),
    path("cart/save/", views.save_cart_view, name="save_cart"),
    path("cart/update/", views.update_cart_view, name="update_cart"),
    path("order/", views.place_order, name="place_order"),
]
