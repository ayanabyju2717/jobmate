from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Skill(models.Model):
    """Skills that employees can possess."""
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Custom User model with role-based access."""
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin_user(self):
        return self.role == 'admin'

    @property
    def is_employee(self):
        return self.role == 'employee'

    @property
    def is_customer(self):
        return self.role == 'customer'


class EmployeeProfile(models.Model):
    """Extended profile for employees with skills, rates, and availability."""
    AVAILABILITY_CHOICES = (
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('offline', 'Offline'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    skills = models.ManyToManyField(Skill, blank=True, related_name='employees')
    bio = models.TextField(blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monthly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    availability = models.CharField(max_length=10, choices=AVAILABILITY_CHOICES, default='available')
    experience_years = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0,
                                     validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_jobs = models.PositiveIntegerField(default=0)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Employee: {self.user.get_full_name() or self.user.username}"

    def update_rating(self):
        """Recalculate average rating from all completed booking reviews."""
        from bookings.models import Review
        reviews = Review.objects.filter(booking__employee=self.user, rating__isnull=False)
        if reviews.exists():
            self.avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.save(update_fields=['avg_rating'])


class CustomerProfile(models.Model):
    """Extended profile for customers with hiring history."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    company_name = models.CharField(max_length=200, blank=True)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_bookings = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Customer: {self.user.get_full_name() or self.user.username}"
