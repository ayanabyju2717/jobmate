"""Signals for notification system – fires on booking status changes."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from .models import Booking, Review


@receiver(post_save, sender=Booking)
def booking_status_notification(sender, instance, created, **kwargs):
    """Send email/log when a booking is created or its status changes."""
    if created:
        subject = f"[JobMate] New Booking Request: {instance.title}"
        message = (
            f"Hi {instance.employee.get_full_name() or instance.employee.username},\n\n"
            f"You have a new booking request from "
            f"{instance.customer.get_full_name() or instance.customer.username}.\n"
            f"Duration: {instance.duration_value} {instance.get_duration_type_display()}\n"
            f"Total Cost: ${instance.total_cost}\n\n"
            f"Please log in to accept or reject."
        )
    else:
        subject = f"[JobMate] Booking #{instance.pk} status → {instance.get_status_display()}"
        message = (
            f"Booking \"{instance.title}\" is now {instance.get_status_display()}.\n"
            f"Check your dashboard for details."
        )

    recipients = [instance.customer.email, instance.employee.email]
    recipients = [r for r in recipients if r]  # filter blanks

    try:
        if recipients:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=True)
    except Exception:
        pass  # graceful degradation – log in production


@receiver(post_save, sender=Review)
def review_notification(sender, instance, created, **kwargs):
    """Notify employee when a review is posted."""
    if created:
        employee = instance.booking.employee
        if employee.email:
            send_mail(
                f"[JobMate] New {instance.rating}★ Review",
                f"You received a review for \"{instance.booking.title}\":\n\n"
                f"\"{instance.comment}\"\n\nRating: {instance.rating}/5",
                settings.DEFAULT_FROM_EMAIL,
                [employee.email],
                fail_silently=True,
            )
