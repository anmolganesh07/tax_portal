from django.urls import path
from .views import (
    ClientSignUpView, CASignUpView,CustomLoginView, CustomLogoutView,
)

urlpatterns = [
    path('signup/client/', ClientSignUpView.as_view(), name='client_signup'),
    path('signup/ca/', CASignUpView.as_view(), name='ca_signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]
