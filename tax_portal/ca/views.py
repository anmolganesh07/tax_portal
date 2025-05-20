from django.views import View
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.utils.crypto import get_random_string
from clients.models import Document, FiledReturn
from accounts.models import User
from django.utils.timezone import now
import calendar
from datetime import datetime
from collections import defaultdict
from django.urls import reverse


class CADashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'ca/CAdashboard.html'

    def test_func(self):
        return self.request.user.role == 'ca' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from datetime import date
        from django.urls import reverse
        context['clients'] = User.objects.filter(assigned_ca=self.request.user, role='client')
        months = [5, 6, 7]
        year = 2025
        return_types = [
            {'type': 'GSTR-1', 'label': 'GSTR-1', 'day': 11},
            {'type': 'GSTR-3B', 'label': 'GSTR-3B', 'day': 20},
            {'type': 'IT', 'label': 'Income Tax', 'day': 30},
        ]
        today = date.today()
        calendar_data = {}
        for client in context['clients']:
            client_returns = []
            for month in months:
                for rt in return_types:
                    if rt['type'] == 'IT' and month != 7:
                        continue
                    due_date = date(year, month, rt['day'])
                    filed_obj = FiledReturn.objects.filter(client=client, return_type=rt['type'], due_date=due_date).first()
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
                    file_url = reverse('file_return') + f'?client_id={client.id}&return_type={rt["type"]}&due_date={due_date}'
                    client_returns.append({
                        'label': rt['label'],
                        'due_date': due_date,
                        'status': status,
                        'color': color,
                        'filed': filed,
                        'filed_date': filed_date,
                        'file_url': file_url,
                        'filed_return_id': filed_return_id,
                    })
            calendar_data[client.username] = client_returns
        context['calendar_data'] = calendar_data
        return context


class CAClientDetailView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'ca/client_detail.html'

    def test_func(self):
        return self.request.user.role == 'ca'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = get_object_or_404(User, id=self.kwargs['pk'], role='client', assigned_ca=self.request.user)
        context['client'] = client
        context['documents'] = Document.objects.filter(client=client).order_by('-uploaded_at')
        return context



class FileReturnView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role == 'ca'

    def get(self, request):
        return_type = request.GET.get('return_type')
        if return_type == 'IT':
            return redirect(reverse('itr_home'))
        return redirect('/')

    def post(self, request):
        client_id = request.POST.get('client_id')
        return_type = request.POST.get('return_type')
        due_date = request.POST.get('due_date')
        client = User.objects.get(id=client_id)
        due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
        FiledReturn.objects.get_or_create(
            client=client,
            return_type=return_type,
            due_date=due_date_obj,
            defaults={'filed_by': request.user}
        )
        messages.success(request, 'Return marked as filed!')
        return redirect(request.META.get('HTTP_REFERER', '/'))


class CAAcknowledgmentView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'accounts/acknowledgment.html'

    def test_func(self):
        return self.request.user.role == 'ca'

    def get(self, request, *args, **kwargs):
        filed_return_id = self.request.GET.get('filed_return_id')
        client_id = self.request.GET.get('client_id')
        if filed_return_id:
            filed_return = get_object_or_404(FiledReturn, id=filed_return_id)
            user = filed_return.client
        elif client_id:
            user = get_object_or_404(User, id=client_id)
            filed_return = FiledReturn.objects.filter(client=user, return_type='IT').order_by('-filed_date').first()
        else:
            return redirect('ca_dashboard')
        context = {
            'assessment_year': '2024-25',
            'name': user.get_full_name() or user.username,
            'pan': getattr(user, 'pan_number', ''),
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
