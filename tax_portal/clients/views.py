from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Document, FiledReturn
from .forms import DocumentUploadForm
from django.utils import timezone
from datetime import date
from django.shortcuts import render, get_object_or_404
from accounts.models import User
from django.utils.crypto import get_random_string

class ClientDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'clients/dashboard.html'

    def test_func(self):
        return self.request.user.role == 'client'  
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from datetime import date
        user = self.request.user
        calendar_returns = []
        months = [5, 6, 7]
        year = 2025
        today = date.today()
        return_types = [
            {'type': 'GSTR-1', 'label': 'GSTR-1', 'day': 11},
            {'type': 'GSTR-3B', 'label': 'GSTR-3B', 'day': 20},
            {'type': 'IT', 'label': 'Income Tax', 'day': 30},
        ]
        for month in months:
            for rt in return_types:
                if rt['type'] == 'IT' and month != 7:
                    continue  
                due_date = date(year, month, rt['day'])
                filed_obj = FiledReturn.objects.filter(client=user, return_type=rt['type'], due_date=due_date).first()
                if filed_obj:
                    status = 'filed'
                    color = 'green'
                    filed = True
                    filed_date = filed_obj.filed_date
                    filed_return_id = filed_obj.id
                elif due_date < today:
                    status = 'overdue'
                    color = 'red'
                    filed = False
                    filed_date = None
                    filed_return_id = ''
                else:
                    status = 'pending'
                    color = 'yellow'
                    filed = False
                    filed_date = None
                    filed_return_id = ''
                calendar_returns.append({
                    'label': rt['label'],
                    'due_date': due_date,
                    'status': status,
                    'color': color,
                    'filed': filed,
                    'filed_date': filed_date,
                    'filed_return_id': filed_return_id,
                })
        months = ['May', 'June', 'July']
        context['calendar_returns'] = calendar_returns
        context['months'] = months
        context['returns'] = []
        return context


class DocumentUploadView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Document
    form_class = DocumentUploadForm
    template_name = 'clients/upload.html'
    success_url = reverse_lazy('client_dashboard')

    def form_valid(self, form):
        form.instance.client = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.role == 'client'
    

class ClientDocumentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Document
    template_name = 'clients/document_list.html' 
    context_object_name = 'documents'
    paginate_by = 10  

    def test_func(self):
        return self.request.user.role == 'client'

    def get_queryset(self):
        return Document.objects.filter(client=self.request.user).order_by('-uploaded_at')

class ClientAcknowledgmentView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'accounts/acknowledgment.html'

    def test_func(self):
        return self.request.user.role == 'client'

    def get(self, request, *args, **kwargs):
        filed_return_id = self.request.GET.get('filed_return_id')
        if filed_return_id:
            filed_return = get_object_or_404(FiledReturn, id=filed_return_id, client=request.user)
        else:
            filed_return = FiledReturn.objects.filter(client=request.user, return_type='IT').order_by('-filed_date').first()
        user = request.user
        context = {
            'assessment_year': '2024-25',
            'name': user.get_full_name() or user.username,
            'pan': getattr(user, 'pan_number', ''),
            'flat_no': user.address if hasattr(user, 'address') else '',
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
