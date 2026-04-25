from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=100)
    location = models.CharField(max_length=50)
    image = models.ImageField(upload_to="media/")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name="%(class)s")

    class Meta:
        abstract = True


class LostItem(Item):
    status = models.CharField(max_length=10, default="Lost")
    postedby = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lost_posts")


class FoundItem(Item):
    status = models.CharField(max_length=10, default="Found")
    postedby = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="found_posts")


def validateemail(email):
    if not email.endswith('@nu.edu.pk'):
        raise ValidationError("only NU id is allowed")

class User(AbstractUser):
    name = models.CharField(max_length=50)
    username = models.CharField(max_length=15, unique=True)
    email = models.EmailField(max_length=50, unique=True, validators=[validateemail])

    REQUIRED_FIELDS = ["email", "name"]


class Category(models.Model):
    name = models.CharField(max_length=50)


class Claim(models.Model):
    STATUS_PENDING = "Pending"
    STATUS_ACCEPTED = "Accepted"
    STATUS_REJECTED = "Rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
    ]
    proof = models.TextField(max_length=100)
    image = models.ImageField(upload_to="media", blank=True, null=True)
    requestby = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="claimrequests")
    found_item = models.ForeignKey(FoundItem, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)


class Notification(models.Model):
    title = models.CharField(max_length=100, default="Claim Request")
    message = models.TextField(default="")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    claimreq = models.ForeignKey(Claim, on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_notifications")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_notifications")

    def __str__(self):
        return self.title


    


