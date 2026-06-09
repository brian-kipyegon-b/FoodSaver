from django.contrib import admin
from . models import FoodItem, Activity, Order

# Register your models here.
admin.site.register(FoodItem)
admin.site.register(Activity)
admin.site.register(Order)