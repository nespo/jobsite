from django.contrib import admin
from pages.models import User, UserInfo


@admin.register(User)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_company')
    list_filter = ('is_company',)

@admin.register(UserInfo)
class UserAdmin(admin.ModelAdmin):
    pass