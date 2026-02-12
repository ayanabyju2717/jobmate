from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Skill, EmployeeProfile, CustomerProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('JobMate', {'fields': ('role', 'phone', 'address', 'city', 'profile_picture')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('JobMate', {'fields': ('role', 'phone', 'city')}),
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'category')


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'availability', 'avg_rating', 'total_jobs', 'is_verified')
    list_filter = ('availability', 'is_verified')
    filter_horizontal = ('skills',)


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'total_bookings', 'total_spent')
