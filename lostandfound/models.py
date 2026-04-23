from django.db import models
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError

# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=100)
    location = models.CharField(max_length=50)
    image = models.ImageField(upload_to="media/")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="%(class)s")
    postedby = models.ForeignKey(User, on_delete=models.CASCADE,  related_name="posts")

    class Meta:
        abstract = True


class LostItem(Item):
    status = models.CharField(max_length=10)

    def __init__(self):
        self.status = "Lost"


class FoundItem(Item):
    status = models.CharField(max_length=10)

    def __init__(self):
        self.status = "Found"


postedby = models.OneToOneField(User, related_name="user")
def validateemail(email):
    if not email.endswith('@nu.edu.pk'):
        raise ValidationError("only NU id is allowed")

class User(models.Model):
    name = models.CharField(max_length=50)
    useranme = models.CharField(max_length=15, unique=True)
    email = models.EmailField(max_length=50, unique=True, validators=[validateemail])
    password = models.CharField(max_length=1, validators=[MinLengthValidator(8)]) 


class Category(models.Model):
    name = models.CharField(max_length=50)


class Claim(models.Model):
    proof = models.TextField(max_length=100)
    image = models.ImageField(upload_to="/media")
    requestby = models.ForeignKey(User, on_delete=models.CASCADE, related_name="claimrequests")
    found_item = models.ForeignKey(FoundItem, on_delete=models.CASCADE)
    status = models.CharField(max_length=10)


class Notification(models.Model):
    title = "Claim Request"
    claimreq = models.ForeignKey(Claim, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)


    


