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
        # Get the filed return by id or by due date/type
        filed_return_id = self.request.GET.get('filed_return_id')
        if filed_return_id:
            filed_return = get_object_or_404(FiledReturn, id=filed_return_id, client=request.user)
        else:
            # fallback: show latest IT return
            filed_return = FiledReturn.objects.filter(client=request.user, return_type='IT').order_by('-filed_date').first()
        user = request.user
        context = {
            'assessment_year': '2025-26',
            'name': user.get_full_name() or user.username,
            'pan': getattr(user, 'pan_number', ''),
            'flat_no': user.address if hasattr(user, 'address') else '',
            'building': '',
            'street': '',
            'area': user.bank_account if hasattr(user, 'bank_account') else '',
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
        return render(request, self.template_name, context)
