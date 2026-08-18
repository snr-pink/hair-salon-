from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("book/", views.book_appointment, name="book_appointment"),
    path("my-appointments/", views.my_appointments, name="my_appointments"),
    path("my-appointments/<int:pk>/cancel/", views.cancel_appointment, name="cancel_appointment"),
    path("stylist-schedule/", views.stylist_schedule, name="stylist_schedule"),
]
