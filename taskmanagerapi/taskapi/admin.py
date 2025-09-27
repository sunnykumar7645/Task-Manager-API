from django.contrib import admin
from taskapi.models import User
from .models import Task
from django.contrib.auth.admin import UserAdmin 

# Register your models here.

class UserModelAdmin(UserAdmin):
    list_display = ('id', 'email', 'name', 'is_admin', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_admin', 'name', 'email')

    fieldsets = (
        ('User Credential', {"fields": ('email', 'password')}),
        ('Personal info', {"fields": ('name',)}),   # <-- tuple
        ('Permission', {"fields": ('is_admin',)}),  # <-- tuple
    )

    search_fields = ('email',)
    ordering = ('email', 'id')
    filter_horizontal = ()

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'is_admin', 'password1', 'password2'), 
        }),
    )



@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id","user", "title","description", "completed", "created_at", "updated_at")
    list_filter = ("completed", "created_at")
    search_fields = ("title", "description")
    ordering = ("-created_at",)

admin.site.register(User, UserModelAdmin)


