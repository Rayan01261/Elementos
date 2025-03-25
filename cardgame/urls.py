from django.urls import path
from . import views

app_name = 'cardgame'

urlpatterns = [
    path("", views.index, name="index"),
    path("hub/", views.goToHub, name="goToHub")
]