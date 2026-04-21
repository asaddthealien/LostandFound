from django.contrib import admin
from .models import Item, LostItem, FoundItem

# Register your models here.
admin.site.register(Item)
admin.site.register(LostItem)
admin.site.register(FoundItem)