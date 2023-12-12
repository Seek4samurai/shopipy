from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login_customer"),
    path("refresh-token/", views.RefreshTokenView.as_view(), name="refresh_token"),
    path("signup/", views.SignupView.as_view(), name="signup_customer"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("cart/", views.FetchCart.as_view(), name="fetch_cart"),
    path("cart_data/", views.FetchCartData.as_view(), name="fetch_cart_data"),
    path("cart/save/", views.SaveCartView.as_view(), name="save_cart"),
    path("cart/update/", views.UpdateCartView.as_view(), name="update_cart"),
    path("order/", views.PlaceOrder.as_view(), name="place_order"),
]
