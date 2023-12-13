from django.urls import path
from . import views


urlpatterns = [
    path("", views.FetchProducts.as_view(), name="fetch_all_products"),
    path(
        "guest/", views.UnAuthFetchProducts.as_view(), name="fetch_all_products_guest"
    ),  # unAuthenticated API for products
    path("item/<uuid:id>/", views.FetchItem.as_view(), name="fetch_item"),
    path(
        "filter/<str:item_type>/<str:category>/<str:gender>/<str:sort_by>/search/",
        views.filter_products,
        name="filter_products",
    ),
]
