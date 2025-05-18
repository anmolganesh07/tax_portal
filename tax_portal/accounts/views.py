from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView
from django.contrib.auth.views import LoginView, LogoutView
from .models import User, ItrUsers
from .forms import ClientSignUpForm, CASignUpForm, LoginForm, ItrUserSignUpForm, ItrUserLoginForm
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate

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


class ItrUserSignUpView(CreateView):
    model = ItrUsers
    form_class = ItrUserSignUpForm
    template_name = 'accounts/itr_signup.html'
    success_url = reverse_lazy('login_itr')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.username = form.cleaned_data['user_id']
        user.save()
        return super().form_valid(form)


class ItrUserLoginView(FormView):
    template_name = 'accounts/itr_login.html'
    form_class = ItrUserLoginForm
    success_url = reverse_lazy('itr_home')

    def form_valid(self, form):
        user_id = form.cleaned_data['user_id']
        password = form.cleaned_data['password']
        user = authenticate(self.request, username=user_id, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
