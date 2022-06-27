from argparse import Namespace
from django.urls import include, path
from . import views


app_name = 'marcarExame'

urlpatterns = [
    path("", views.login_view, name="login_view"),
    path("dash", views.dash, name="dash"),
    path("register", views.register, name="register"),
    path("logout_user", views.logout_user, name="logout_user"),
    path("about", views.about, name="about"),
    path("registerMedic", views.registerMedic, name="registerMedic"),
    path("createAppointments", views.createAppointments, name="createAppointments"),
    path("pastAppointments", views.pastAppointments, name="pastAppointments"),
    path("scheduleAppointments", views.scheduleAppointments, name="scheduleAppointments"),
    path("futureAppointments", views.futureAppointments, name="futureAppointments"),
    path("myAppointments", views.myAppointments, name="myAppointments"),
    path("myAvailability", views.myAvailability, name="myAvailability"),
    path("<int:appointment_id>/addResult", views.addResult, name="addResult"),
    path("<int:appointment_id>/removeAppointment", views.removeAppointment, name="removeAppointment"),
    path("<int:appointment_id>/joinAppointment", views.joinAppointment, name="joinAppointment"),
    path("reviews", views.reviews, name="reviews")
]
