from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("itempost", views.itempost, name="itempost"),
    path("listitems/<str:status>", views.listitems, name="listitems"),
    path("login", views.loginview, name="login"),
    path("register", views.registerview, name="register"),
    path("logout", views.logoutview, name="logout"),
]