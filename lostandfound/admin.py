from django.contrib import admin
from .models import Item, LostItem, FoundItem, User

# Register your models here.
admin.site.register(LostItem)
admin.site.register(FoundItem)
admin.site.register(User)