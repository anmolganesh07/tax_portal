from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView
from django.contrib.auth.views import LoginView, LogoutView
from .models import User
from .forms import ClientSignUpForm, CASignUpForm, LoginForm
from django.shortcuts import redirect
from django.contrib.auth import login

class ClientSignUpView(CreateView):
    model = User
    form_class = ClientSignUpForm
    template_name = 'accounts/client_signup.html'
    success_url = reverse_lazy('client_dashboard')

    def form_valid(self, form):
        form.instance.role = 'client'
        return super().form_valid(form)


class CASignUpView(CreateView):
    model = User
    form_class = CASignUpForm
    template_name = 'accounts/ca_signup.html'
    success_url = reverse_lazy('ca_dashboard')

    def form_valid(self, form):
        form.instance.role = 'ca'
        response = super().form_valid(form)
        login(self.request, self.object)  # Log in the new CA user
        return response


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.role == 'client':
            return reverse_lazy('client_dashboard')
        elif user.role == 'ca':
            return reverse_lazy('ca_dashboard')
        return reverse_lazy('home')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')
