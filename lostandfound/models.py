from django.db import models

# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=100)
    location = models.CharField(max_length=50)
    status = models.CharField(max_length=10)
    image = models.ImageField(upload_to="media/")

    def __str__(self):
        return f"{self.name}/n {self.description}\n {self.location}\n"
    
