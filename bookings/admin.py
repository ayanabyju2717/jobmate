from django.contrib import admin
from .models import Booking, Review, WorkProof


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'customer', 'employee', 'status',
                    'duration_type', 'total_cost', 'created_at')
    list_filter = ('status', 'duration_type')
    search_fields = ('title', 'customer__username', 'employee__username')
    filter_horizontal = ('skills_required',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('booking', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating',)


@admin.register(WorkProof)
class WorkProofAdmin(admin.ModelAdmin):
    list_display = ('booking', 'uploaded_by', 'created_at')
    list_filter = ('created_at',)
