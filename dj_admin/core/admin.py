from django.contrib import admin
from .models import Subscribtion, TGUsers, UserCRM, PurchasedSubscriptions

@admin.register(Subscribtion)
class Subscribtion_Admin(admin.ModelAdmin):
    list_display = Subscribtion.list_display()
