#urls.py
from django.urls import path
from .views import Rr_3_parameters, main_form_parameters,stability_coefficients
from . import views
urlpatterns = [
    path("", Rr_3_parameters, name='Rr_3_parameters'),
    path("main_form_parameters/", main_form_parameters, name='main_form_parameters'),
    path("main_form_parameters/stability_coefficients/", stability_coefficients, name='stability_coefficients'),


]
