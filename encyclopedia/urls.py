from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:entry>", views.entries, name="entries"),
    path("add", views.add, name="add"),
    path("change/<str:title>", views.change, name="change"),
    path("search", views.search, name="search"),
    path("random_page", views.random_page, name="random_page")
]
