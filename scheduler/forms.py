from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Appointment, CustomerProfile


class CustomerSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "phone_number"]

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            CustomerProfile.objects.create(
                user=user, phone_number=self.cleaned_data.get("phone_number", "")
            )
        return user


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["stylist", "service", "date", "start_time", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["stylist"].queryset = self.fields["stylist"].queryset.filter(is_active=True)
        self.fields["service"].queryset = self.fields["service"].queryset.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        # Build a throwaway instance so we can reuse the model's own
        # validation (working hours + double-booking checks) at the form level.
        instance = Appointment(
            customer=self.instance.customer if self.instance.pk else None,
            stylist=cleaned_data.get("stylist"),
            service=cleaned_data.get("service"),
            date=cleaned_data.get("date"),
            start_time=cleaned_data.get("start_time"),
        )
        if instance.stylist_id and instance.service_id and instance.date and instance.start_time:
            try:
                instance.clean()
            except forms.ValidationError as e:
                raise forms.ValidationError(e.message)
        return cleaned_data
