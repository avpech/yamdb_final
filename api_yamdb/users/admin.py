from django.contrib import admin
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'role',
        'bio',
    )
    search_fields = ('username', 'email')
    list_filter = ('role',)
    empty_value_display = '-пусто-'
