from django.contrib import admin

from .models import User, Subscribe

EMPTY_VALUE = '-пусто-'

class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'first_name', 'last_name', 'email', 'password'
    )
    search_fields = ('username', 'first_name', 'last_name')
    list_filter = ('username', 'email')
    empty_value_display = EMPTY_VALUE


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = EMPTY_VALUE


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscriptionAdmin)
