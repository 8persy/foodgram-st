from django.contrib import admin
from .models import User, Subscription
from django.conf import settings


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'email', 'username',
                    'first_name', 'last_name', 'avatar')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')
    empty_value_display = settings.EMPTY_VALUE


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    empty_value_display = settings.EMPTY_VALUE
