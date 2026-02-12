from django import forms
from .models import Booking, Review, WorkProof
from accounts.models import Skill


class BookingForm(forms.ModelForm):
    skills_required = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Booking
        fields = ['title', 'description', 'skills_required', 'duration_type',
                  'duration_value', 'start_date', 'end_date', 'location']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }


class WorkProofForm(forms.ModelForm):
    class Meta:
        model = WorkProof
        fields = ['description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by skill, location, or name…',
        }),
    )
