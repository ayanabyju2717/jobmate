from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, EmployeeProfile, CustomerProfile, Skill


class SignUpForm(UserCreationForm):
    """Registration form that also picks a role."""
    role = forms.ChoiceField(choices=[('employee', 'Employee'), ('customer', 'Customer')])
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'city',
                  'role', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'profile_picture']


class EmployeeProfileForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = EmployeeProfile
        fields = ['bio', 'skills', 'hourly_rate', 'daily_rate', 'monthly_rate',
                  'availability', 'experience_years', 'latitude', 'longitude']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['company_name']
