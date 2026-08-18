from datetime import datetime, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Stylist(models.Model):
    """A staff member who performs services and can be booked for appointments."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stylist_profile",
        null=True,
        blank=True,
        help_text="Optional linked login account for this stylist.",
    )
    name = models.CharField(max_length=120)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="stylists/", blank=True, null=True)
    work_start = models.TimeField(default="09:00")
    work_end = models.TimeField(default="17:00")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Service(models.Model):
    """A service the salon offers, e.g. Haircut, Coloring."""
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(help_text="How long this service takes, in minutes.")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.duration_minutes} min)"


class CustomerProfile(models.Model):
    """Extra info attached to a customer's user account."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )
    phone_number = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.user.get_username()


class Appointment(models.Model):
    """A booking of a customer with a stylist for a service at a given date/time."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        CANCELLED = "CANCELLED", "Cancelled"
        COMPLETED = "COMPLETED", "Completed"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="appointments"
    )
    stylist = models.ForeignKey(Stylist, on_delete=models.CASCADE, related_name="appointments")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="appointments")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(editable=False, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.customer} with {self.stylist} on {self.date} {self.start_time}"

    def _compute_end_time(self):
        start_dt = datetime.combine(self.date, self.start_time)
        end_dt = start_dt + timedelta(minutes=self.service.duration_minutes)
        return end_dt.time()

    def clean(self):
        if not self.date or not self.start_time or not self.stylist_id or not self.service_id:
            return

        self.end_time = self._compute_end_time()

        # Must fall within the stylist's working hours.
        if self.start_time < self.stylist.work_start or self.end_time > self.stylist.work_end:
            raise ValidationError(
                f"{self.stylist.name} is only available between "
                f"{self.stylist.work_start} and {self.stylist.work_end}."
            )

        # Prevent double-booking: overlap check against existing active appointments
        # for the same stylist on the same date.
        overlapping = Appointment.objects.filter(
            stylist=self.stylist,
            date=self.date,
        ).exclude(status=self.Status.CANCELLED)

        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        for other in overlapping:
            other_end = other.end_time or other._compute_end_time()
            if self.start_time < other_end and other.start_time < self.end_time:
                raise ValidationError(
                    f"{self.stylist.name} is already booked from "
                    f"{other.start_time.strftime('%H:%M')} to {other_end.strftime('%H:%M')} "
                    f"on {self.date}. Please choose another time."
                )

    def save(self, *args, **kwargs):
        self.end_time = self._compute_end_time()
        self.full_clean()
        super().save(*args, **kwargs)
