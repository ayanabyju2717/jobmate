from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Booking(models.Model):
    """Core booking model linking customer, employee, duration, cost, and status."""
    DURATION_CHOICES = (
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings_as_customer'
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings_as_employee'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    skills_required = models.ManyToManyField('accounts.Skill', blank=True)
    duration_type = models.CharField(max_length=10, choices=DURATION_CHOICES, default='hourly')
    duration_value = models.PositiveIntegerField(default=1, help_text="Number of hours/days/months")
    rate_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking #{self.pk}: {self.title} ({self.get_status_display()})"

    def calculate_cost(self):
        """Pricing Engine: Rate × Duration."""
        if self.employee and hasattr(self.employee, 'employee_profile'):
            profile = self.employee.employee_profile
            rate_map = {
                'hourly': profile.hourly_rate,
                'daily': profile.daily_rate,
                'monthly': profile.monthly_rate,
            }
            self.rate_applied = rate_map.get(self.duration_type, 0)
            self.total_cost = self.rate_applied * self.duration_value
        return self.total_cost

    def save(self, *args, **kwargs):
        if not self.total_cost:
            self.calculate_cost()
        super().save(*args, **kwargs)


class Review(models.Model):
    """Post-job feedback linked to a booking."""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given'
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for Booking #{self.booking.pk} – {self.rating}★"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the employee's average rating
        if hasattr(self.booking.employee, 'employee_profile'):
            self.booking.employee.employee_profile.update_rating()


class WorkProof(models.Model):
    """Progress tracking – employees upload proof of work."""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='work_proofs')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField()
    image = models.ImageField(upload_to='work_proofs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"WorkProof for Booking #{self.booking.pk}"
