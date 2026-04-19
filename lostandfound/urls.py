from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("itempost", views.itempost, name="itempost"),
    path("listitems/<str:status>", views.listitems, name="listitems"),
]