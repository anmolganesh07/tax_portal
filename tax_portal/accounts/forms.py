from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class ClientSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'assigned_ca']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_ca'].queryset = User.objects.filter(role='ca')


class CASignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    pass
