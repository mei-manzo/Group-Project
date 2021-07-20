from django.urls import path     
from . import views
urlpatterns = [
    path('', views.index),
    path('success', views.success),
    path('check_registration', views.check_registration),
    path('check_login', views.check_login),
    path('logout', views.logout),
]