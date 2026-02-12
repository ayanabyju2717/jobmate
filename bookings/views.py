from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import Booking, Review, WorkProof
from .forms import BookingForm, ReviewForm, WorkProofForm, SearchForm
from .services import rank_employees, smart_search, calculate_booking_cost
from accounts.models import User, EmployeeProfile


def home_view(request):
    """Landing page with search and top-rated employees."""
    form = SearchForm(request.GET or None)
    employees = []
    query = ''
    if form.is_valid():
        query = form.cleaned_data.get('q', '')
    if query:
        profiles = smart_search(query)
    else:
        profiles = EmployeeProfile.objects.filter(
            availability='available'
        ).select_related('user').prefetch_related('skills').order_by('-avg_rating')[:12]
    return render(request, 'bookings/home.html', {
        'form': form,
        'profiles': profiles,
        'query': query,
    })


@login_required
def employee_list_view(request):
    """Browse/search employees with AI matching."""
    form = SearchForm(request.GET or None)
    query = ''
    results = []
    if form.is_valid():
        query = form.cleaned_data.get('q', '')
    if query:
        profiles = smart_search(query)
        results = [{'profile': p, 'score': None, 'breakdown': None} for p in profiles]
    else:
        results = rank_employees()
    return render(request, 'bookings/employee_list.html', {
        'form': form,
        'results': results,
        'query': query,
    })


@login_required
def create_booking_view(request, employee_pk):
    """Customer creates a booking for a chosen employee."""
    if not request.user.is_customer:
        return HttpResponseForbidden("Only customers can create bookings.")
    employee_user = get_object_or_404(User, pk=employee_pk, role='employee')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.employee = employee_user
            booking.calculate_cost()
            booking.save()
            form.save_m2m()
            messages.success(request, f'Booking created! Estimated cost: ${booking.total_cost}')
            return redirect('booking_detail', pk=booking.pk)
    else:
        form = BookingForm()

    profile = employee_user.employee_profile
    return render(request, 'bookings/create_booking.html', {
        'form': form,
        'employee': employee_user,
        'profile': profile,
    })


@login_required
def booking_detail_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.user != booking.customer and request.user != booking.employee and not request.user.is_admin_user:
        return HttpResponseForbidden()
    work_proofs = booking.work_proofs.all()
    review = getattr(booking, 'review', None)
    return render(request, 'bookings/booking_detail.html', {
        'booking': booking,
        'work_proofs': work_proofs,
        'review': review,
    })


@login_required
def booking_list_view(request):
    """List bookings for the logged-in user."""
    user = request.user
    if user.is_customer:
        bookings = Booking.objects.filter(customer=user)
    elif user.is_employee:
        bookings = Booking.objects.filter(employee=user)
    else:
        bookings = Booking.objects.all()
    return render(request, 'bookings/booking_list.html', {'bookings': bookings})


@login_required
def booking_action_view(request, pk, action):
    """Employee accepts/rejects or marks booking in_progress/completed."""
    booking = get_object_or_404(Booking, pk=pk)
    allowed_actions = {
        'accept': ('pending', 'accepted'),
        'reject': ('pending', 'rejected'),
        'start': ('accepted', 'in_progress'),
        'complete': ('in_progress', 'completed'),
        'cancel': (None, 'cancelled'),
    }
    if action not in allowed_actions:
        return HttpResponseForbidden("Invalid action.")

    required_status, new_status = allowed_actions[action]

    # Validate permission
    if action in ('accept', 'reject', 'start', 'complete'):
        if request.user != booking.employee:
            return HttpResponseForbidden()
    if action == 'cancel':
        if request.user != booking.customer and request.user != booking.employee:
            return HttpResponseForbidden()

    if required_status and booking.status != required_status:
        messages.error(request, f"Cannot {action} a booking that is {booking.get_status_display()}.")
        return redirect('booking_detail', pk=pk)

    booking.status = new_status
    booking.save()

    # Update employee stats on completion
    if new_status == 'completed' and hasattr(booking.employee, 'employee_profile'):
        ep = booking.employee.employee_profile
        ep.total_jobs += 1
        ep.save(update_fields=['total_jobs'])
        # Update customer stats
        if hasattr(booking.customer, 'customer_profile'):
            cp = booking.customer.customer_profile
            cp.total_bookings += 1
            cp.total_spent += booking.total_cost
            cp.save(update_fields=['total_bookings', 'total_spent'])

    messages.success(request, f"Booking {action}ed successfully.")
    return redirect('booking_detail', pk=pk)


@login_required
def add_review_view(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, status='completed')
    if request.user != booking.customer:
        return HttpResponseForbidden("Only the customer can review.")
    if hasattr(booking, 'review'):
        messages.info(request, "You already reviewed this booking.")
        return redirect('booking_detail', pk=booking_pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.reviewer = request.user
            review.save()
            messages.success(request, 'Review submitted!')
            return redirect('booking_detail', pk=booking_pk)
    else:
        form = ReviewForm()
    return render(request, 'bookings/add_review.html', {'form': form, 'booking': booking})


@login_required
def add_work_proof_view(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk)
    if request.user != booking.employee:
        return HttpResponseForbidden("Only the assigned employee can upload work proof.")
    if booking.status not in ('accepted', 'in_progress'):
        messages.error(request, "Work proof can only be uploaded for active bookings.")
        return redirect('booking_detail', pk=booking_pk)

    if request.method == 'POST':
        form = WorkProofForm(request.POST, request.FILES)
        if form.is_valid():
            proof = form.save(commit=False)
            proof.booking = booking
            proof.uploaded_by = request.user
            proof.save()
            messages.success(request, 'Work proof uploaded.')
            return redirect('booking_detail', pk=booking_pk)
    else:
        form = WorkProofForm()
    return render(request, 'bookings/add_work_proof.html', {'form': form, 'booking': booking})
