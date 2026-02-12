from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from accounts.models import User, EmployeeProfile
from bookings.models import Booking, Review


@login_required
def admin_dashboard_view(request):
    """Admin analytics dashboard."""
    if not request.user.is_admin_user:
        return HttpResponseForbidden("Admin access only.")

    now = timezone.now()
    last_30_days = now - timedelta(days=30)

    # Counts
    total_users = User.objects.count()
    total_employees = User.objects.filter(role='employee').count()
    total_customers = User.objects.filter(role='customer').count()
    pending_verifications = EmployeeProfile.objects.filter(is_verified=False).count()

    # Bookings stats
    total_bookings = Booking.objects.count()
    bookings_by_status = dict(
        Booking.objects.values_list('status').annotate(c=Count('id')).values_list('status', 'c')
    )
    recent_bookings = Booking.objects.filter(created_at__gte=last_30_days)
    revenue = Booking.objects.filter(status='completed').aggregate(
        total=Sum('total_cost'))['total'] or 0

    # Fraud indicators: users with many cancelled/rejected bookings
    fraud_flags = (
        User.objects.annotate(
            cancelled=Count('bookings_as_customer', filter=Q(bookings_as_customer__status='cancelled')),
            rejected=Count('bookings_as_customer', filter=Q(bookings_as_customer__status='rejected')),
        )
        .filter(Q(cancelled__gte=5) | Q(rejected__gte=5))
    )

    # Recent bookings for table
    latest_bookings = Booking.objects.select_related('customer', 'employee').order_by('-created_at')[:20]

    # Unverified employees
    unverified_employees = EmployeeProfile.objects.filter(
        is_verified=False
    ).select_related('user')

    return render(request, 'dashboard/admin_dashboard.html', {
        'total_users': total_users,
        'total_employees': total_employees,
        'total_customers': total_customers,
        'pending_verifications': pending_verifications,
        'total_bookings': total_bookings,
        'bookings_by_status': bookings_by_status,
        'recent_bookings_count': recent_bookings.count(),
        'revenue': revenue,
        'fraud_flags': fraud_flags,
        'latest_bookings': latest_bookings,
        'unverified_employees': unverified_employees,
    })


@login_required
def verify_employee_view(request, pk):
    """Admin approves an employee's registration."""
    if not request.user.is_admin_user:
        return HttpResponseForbidden()
    profile = EmployeeProfile.objects.get(pk=pk)
    profile.is_verified = True
    profile.save(update_fields=['is_verified'])
    from django.contrib import messages
    messages.success(request, f"{profile.user.get_full_name()} verified.")
    return render(request, 'dashboard/admin_dashboard.html', {})
