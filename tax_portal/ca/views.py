from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from clients.models import Document
from accounts.models import User
from django.utils.timezone import now
import calendar
from collections import defaultdict
from clients.models import Document, FiledReturn

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
                    elif due_date < today:
                        status = 'overdue'
                        color = 'red'
                        filed = False
                        filed_date = None
                    else:
                        status = 'pending'
                        color = 'yellow'
                        filed = False
                        filed_date = None
                    file_url = reverse('file_return') + f'?client_id={client.id}&return_type={rt["type"]}&due_date={due_date}'
                    client_returns.append({
                        'label': rt['label'],
                        'due_date': due_date,
                        'status': status,
                        'color': color,
                        'filed': filed,
                        'filed_date': filed_date,
                        'file_url': file_url,
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

from django.views import View
from django.shortcuts import redirect
from django.contrib import messages

class FileReturnView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role == 'ca'
    def post(self, request):
        from datetime import datetime
        client_id = request.POST.get('client_id')
        return_type = request.POST.get('return_type')
        due_date = request.POST.get('due_date')
        from accounts.models import User
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
