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


class ClientPersonalInfoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        instance = kwargs.get('instance', None)
        if instance:
            initial.update({
                'pan_number': instance.pan_number,
                'aadhar_number': instance.aadhar_number,
                'phone_number': instance.phone_number,
                'address': instance.address,
                'bank_account': instance.bank_account,
            })
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)
    class Meta:
        model = User
        fields = ['pan_number', 'aadhar_number', 'phone_number', 'address', 'bank_account']
        widgets = {
            'pan_number': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'aadhar_number': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'address': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
            'bank_account': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2'}),
        }
