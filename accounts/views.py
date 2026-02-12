from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, EmployeeProfile, CustomerProfile
from .forms import SignUpForm, UserUpdateForm, EmployeeProfileForm, CustomerProfileForm


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create the matching profile
            if user.role == 'employee':
                EmployeeProfile.objects.create(user=user)
            else:
                CustomerProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def profile_view(request):
    user = request.user
    context = {'user': user}
    if user.is_employee and hasattr(user, 'employee_profile'):
        context['profile'] = user.employee_profile
        context['skills'] = user.employee_profile.skills.all()
    elif user.is_customer and hasattr(user, 'customer_profile'):
        context['profile'] = user.customer_profile
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit_view(request):
    user = request.user
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if user.is_employee:
            profile_form = EmployeeProfileForm(
                request.POST, instance=user.employee_profile
            )
        else:
            profile_form = CustomerProfileForm(
                request.POST, instance=user.customer_profile
            )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=user)
        if user.is_employee:
            profile_form = EmployeeProfileForm(instance=user.employee_profile)
        else:
            profile_form = CustomerProfileForm(instance=user.customer_profile)

    return render(request, 'accounts/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


def employee_public_profile(request, pk):
    emp_user = get_object_or_404(User, pk=pk, role='employee')
    profile = get_object_or_404(EmployeeProfile, user=emp_user)
    bookings_completed = emp_user.bookings_as_employee.filter(status='completed').count()
    return render(request, 'accounts/employee_public.html', {
        'emp_user': emp_user,
        'profile': profile,
        'bookings_completed': bookings_completed,
    })
