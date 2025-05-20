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
from accounts.models import User


class ClientSignUpView(CreateView):
    model = User
    form_class = ClientSignUpForm
    template_name = 'accounts/client_signup.html'
    success_url = reverse_lazy('client_personal_info')

    def form_valid(self, form):
        form.instance.role = 'client'
        response = super().form_valid(form)
        login(self.request, self.object) 
        return response


class CASignUpView(CreateView):
    model = User
    form_class = CASignUpForm
    template_name = 'accounts/ca_signup.html'
    success_url = reverse_lazy('ca_dashboard')

    def form_valid(self, form):
        form.instance.role = 'ca'
        response = super().form_valid(form)
        login(self.request, self.object)  
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
        client_id = self.request.GET.get('client_id') or self.request.POST.get('client_id')
        user = authenticate(self.request, username=user_id, password=password)
        if user is not None:
            login(self.request, user)
            self.request.session['financial_year'] = financial_year
            if client_id:
                self.request.session['ack_client_id'] = int(client_id)
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class ClientPersonalInfoView(LoginRequiredMixin, FormView):
    template_name = 'accounts/client_personal_info.html'
    form_class = ClientPersonalInfoForm
    success_url = reverse_lazy('login')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
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
        client_id = self.request.GET.get('client_id') or self.request.POST.get('client_id')
        if client_id:
            try:
                client = User.objects.get(id=client_id)
                kwargs['instance'] = client
            except User.DoesNotExist:
                kwargs['instance'] = self.request.user
        else:
            kwargs['instance'] = self.request.user
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'ca':
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
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
        client_id = request.GET.get('client_id') or request.POST.get('client_id')
        if client_id:
            client = get_object_or_404(User, id=client_id)
            due_date = date(2025, 7, 30)
            FiledReturn.objects.get_or_create(
                client=client,
                return_type='IT',
                due_date=due_date,
                defaults={'filed_by': request.user}
            )
            request.session['ack_client_id'] = int(client_id)
        if 'ack_due_date' in request.session:
            del request.session['ack_due_date']
        return redirect('acknowledgment')


class AcknowledgmentView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/acknowledgment.html'

    def get(self, request, *args, **kwargs):
        from accounts.models import User
        from clients.models import FiledReturn
        client_id = request.session.get('ack_client_id') or request.GET.get('client_id')
        user = None
        if client_id:
            try:
                user = User.objects.get(id=client_id)
                due_date = date(2025, 7, 30)
                FiledReturn.objects.get_or_create(
                    client=user,
                    return_type='IT',
                    due_date=due_date,
                    defaults={'filed_by': request.user}
                )
            except User.DoesNotExist:
                user = None
        context = {
            'assessment_year': '2025-26',
            'name': user.get_full_name() or user.username if user else '',
            'pan': getattr(user, 'pan_number', '') if user else '',
            'building': 'Sunshine Apartments',
            'street': 'MG Road',
            'area': 'MG Road',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'pincode': '560097',
            'status': 'Filed',
            'ack_number': get_random_string(12).upper(),
            'gross_total_income': '12,50,000',
            'deductions': '1,50,000',
            'total_income': '11,00,000',
            'deemed_income': '0',
            'current_year_loss': '0',
            'net_tax_payable': '1,10,000',
            'interest_fee': '2,000',
            'total_tax_interest_fee': '1,12,000',
            'advance_tax': '50,000',
            'tds': '40,000',
            'tcs': '5,000',
            'self_assessment_tax': '10,000',
            'total_taxes_paid': '1,05,000',
            'tax_payable': '7,000',
            'refund': '0',
            'exempt_income': '1,00,000',
        }
        return render(request, self.template_name, context)
