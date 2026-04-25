from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("itempost", views.itempost, name="itempost"),
    path("listitems/<str:status>", views.listitems, name="listitems"),
    path("claim/<int:item_id>", views.claim, name="claim"),
    path("notifications", views.notificationsview, name="notifications"),
    path("review/<int:notification_id>", views.reviewclaim, name="review"),
    path("login", views.loginview, name="login"),
    path("register", views.registerview, name="register"),
    path("logout", views.logoutview, name="logout"),
]