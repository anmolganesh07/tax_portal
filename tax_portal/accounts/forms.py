from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, ItrUsers

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


class ItrSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'assigned_ca']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_ca'].queryset = User.objects.filter(role='ca')


class ItrLoginForm(UserCreationForm):
    pass
class LoginForm(AuthenticationForm):
    pass


class ItrUserSignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = ItrUsers
        fields = ['user_id', 'password']


class ItrUserLoginForm(forms.Form):
    user_id = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    FIN_YEAR_CHOICES = [
        (f"{y}-{y+1}", f"{y}-{y+1}") for y in range(2019, 2026)
    ]
    financial_year = forms.ChoiceField(choices=FIN_YEAR_CHOICES, label="Financial Year")
