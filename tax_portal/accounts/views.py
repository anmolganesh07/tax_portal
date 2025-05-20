from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from .models import User, ItrUsers
from .forms import ClientSignUpForm, CASignUpForm, LoginForm, ItrUserSignUpForm, ItrUserLoginForm, ClientPersonalInfoForm
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.shortcuts import render
from clients.models import FiledReturn
from datetime import date
import logging

class ClientSignUpView(CreateView):
    model = User
    form_class = ClientSignUpForm
    template_name = 'accounts/client_signup.html'
    success_url = reverse_lazy('client_personal_info')

    def form_valid(self, form):
        form.instance.role = 'client'
        response = super().form_valid(form)
        login(self.request, self.object)  # Log in the new client user
        return response


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

    def get_success_url(self):
        client_id = self.request.GET.get('client_id')
        if client_id:
            return reverse_lazy('itr_personal_info') + f'?client_id={client_id}'
        return reverse_lazy('itr_personal_info')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_id = self.request.GET.get('client_id') or self.request.POST.get('client_id')
        context['client_id'] = client_id
        return context

    def form_valid(self, form):
        user_id = form.cleaned_data['user_id']
        password = form.cleaned_data['password']
        financial_year = form.cleaned_data['financial_year']
        user = authenticate(self.request, username=user_id, password=password)
        if user is not None:
            login(self.request, user)
            self.request.session['financial_year'] = financial_year
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class ClientPersonalInfoView(LoginRequiredMixin, FormView):
    template_name = 'accounts/client_personal_info.html'
    form_class = ClientPersonalInfoForm
    success_url = reverse_lazy('login')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Do NOT set instance, so the form is always empty for the client
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        user.pan_number = form.cleaned_data['pan_number']
        user.aadhar_number = form.cleaned_data['aadhar_number']
        user.phone_number = form.cleaned_data['phone_number']
        user.address = form.cleaned_data['address']
        user.bank_account = form.cleaned_data['bank_account']
        user.save()
        return super().form_valid(form)


class ItrPersonalInfoView(LoginRequiredMixin, FormView):
    template_name = 'accounts/itr_personal_info.html'
    form_class = ClientPersonalInfoForm
    success_url = reverse_lazy('itr_personal_info')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Only use instance if the user has already saved info (i.e., not a new user with all fields blank)
        user = self.request.user
        if any([
            bool(user.pan_number),
            bool(user.aadhar_number),
            bool(user.phone_number),
            bool(user.address),
            bool(user.bank_account)
        ]):
            kwargs['instance'] = user
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'ca':
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Always save to the current user
        user = self.request.user
        user.pan_number = form.cleaned_data['pan_number']
        user.aadhar_number = form.cleaned_data['aadhar_number']
        user.phone_number = form.cleaned_data['phone_number']
        user.address = form.cleaned_data['address']
        user.bank_account = form.cleaned_data['bank_account']
        user.save()
        return super().form_valid(form)


class SelfDeclarationView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/self_declaration.html'

    def post(self, request, *args, **kwargs):
        # Mark only the IT return as filed for the client after self declaration
        client_id = request.GET.get('client_id') or request.POST.get('client_id')
        if client_id:
            client = get_object_or_404(User, id=client_id)
            # Use the same due date as the dashboard for IT (July 30, 2025)
            due_date = date(2025, 7, 30)
            FiledReturn.objects.get_or_create(
                client=client,
                return_type='IT',
                due_date=due_date,
                defaults={'filed_by': request.user}
            )
            # Set client_id in session for acknowledgment
            request.session['ack_client_id'] = int(client_id)
        # Do NOT clear 'ack_client_id' here!
        if 'ack_due_date' in request.session:
            del request.session['ack_due_date']
        return redirect('acknowledgment')


class AcknowledgmentView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/acknowledgment.html'

    def get(self, request, *args, **kwargs):
        from accounts.models import User
        client_id = request.session.get('ack_client_id')
        due_date_str = request.session.get('ack_due_date')
        if client_id:
            user = User.objects.get(id=client_id)
        else:
            user = request.user
        context = {
            'assessment_year': '2025-26',
            'name': user.get_full_name() or user.username,
            'pan': getattr(user, 'pan_number', ''),
            'flat_no': '',
            'building': '',
            'street': '',
            'area': '',
            'city': '',
            'state': '',
            'pincode': '',
            'status': '',
            'ack_number': get_random_string(12).upper(),
            'gross_total_income': '...',
            'deductions': '...',
            'total_income': '...',
            'deemed_income': '...',
            'current_year_loss': '...',
            'net_tax_payable': '...',
            'interest_fee': '...',
            'total_tax_interest_fee': '...',
            'advance_tax': '...',
            'tds': '...',
            'tcs': '...',
            'self_assessment_tax': '...',
            'total_taxes_paid': '...',
            'tax_payable': '...',
            'refund': '...',
            'exempt_income': '...',
        }
        if hasattr(user, 'address') and user.address:
            context['flat_no'] = user.address
        if hasattr(user, 'bank_account') and user.bank_account:
            context['area'] = user.bank_account
        return render(request, self.template_name, context)
