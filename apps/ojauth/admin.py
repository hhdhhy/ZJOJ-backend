from django.contrib import admin
from .models import OJUser, Class, ClassMember


@admin.register(OJUser)
class OJUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'realname', 'role', 'status', 'is_staff', 'date_joined']
    list_filter = ['role', 'status', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'realname', 'telephone']
    readonly_fields = ['uid', 'date_joined', 'last_login']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('uid', 'username', 'email', 'telephone', 'realname')
        }),
        ('权限信息', {
            'fields': ('password', 'role', 'status', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('个人信息', {
            'fields': ('avatar', 'bio'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'coach', 'create_time']
    search_fields = ['name']
    readonly_fields = ['create_time']


@admin.register(ClassMember)
class ClassMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'class_obj', 'join_time']
    list_filter = ['class_obj']
    search_fields = ['user__username', 'user__realname', 'class_obj__name']
    readonly_fields = ['join_time']
