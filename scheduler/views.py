from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AppointmentForm, CustomerSignUpForm
from .models import Appointment, Service, Stylist


def home(request):
    services = Service.objects.filter(is_active=True)
    stylists = Stylist.objects.filter(is_active=True)
    return render(request, "scheduler/home.html", {"services": services, "stylists": stylists})


def signup(request):
    if request.method == "POST":
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            return redirect("home")
    else:
        form = CustomerSignUpForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def book_appointment(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.customer = request.user
            try:
                appointment.save()
            except ValidationError as e:
                form.add_error(None, e)
            else:
                messages.success(request, "Your appointment has been booked!")
                return redirect("my_appointments")
    else:
        form = AppointmentForm()
    return render(request, "scheduler/book_appointment.html", {"form": form})


@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(customer=request.user)
    return render(request, "scheduler/my_appointments.html", {"appointments": appointments})


@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, customer=request.user)
    if request.method == "POST":
        appointment.status = Appointment.Status.CANCELLED
        appointment.save()
        messages.success(request, "Appointment cancelled.")
        return redirect("my_appointments")
    return render(request, "scheduler/cancel_confirm.html", {"appointment": appointment})


@login_required
def stylist_schedule(request):
    stylist = get_object_or_404(Stylist, user=request.user)
    appointments = Appointment.objects.filter(stylist=stylist).exclude(
        status=Appointment.Status.CANCELLED
    )
    return render(
        request, "scheduler/stylist_schedule.html", {"appointments": appointments, "stylist": stylist}
    )
