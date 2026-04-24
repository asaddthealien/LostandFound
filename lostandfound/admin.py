from django.contrib import admin
from .models import Item, LostItem, FoundItem, User, Notification, Category, Claim

# Register your models here.
admin.site.register(LostItem)
admin.site.register(FoundItem)
admin.site.register(User)
admin.site.register(Notification)
admin.site.register(Category)
admin.site.register(Claim)