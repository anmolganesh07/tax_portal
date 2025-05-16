from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Document, FiledReturn
from .forms import DocumentUploadForm
from django.utils import timezone
from datetime import date

class ClientDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'clients/dashboard.html'

    def test_func(self):
        return self.request.user.role == 'client'  # Only allow Clients
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calendar logic for May, June, July 2025
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
                    continue  # IT return only in July
                due_date = date(year, month, rt['day'])
                filed_obj = FiledReturn.objects.filter(client=user, return_type=rt['type'], due_date=due_date).first()
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
                calendar_returns.append({
                    'label': rt['label'],
                    'due_date': due_date,
                    'status': status,
                    'color': color,
                    'filed': filed,
                    'filed_date': filed_date,
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
    paginate_by = 10  # Optional: paginate if many docs

    def test_func(self):
        return self.request.user.role == 'client'

    def get_queryset(self):
        return Document.objects.filter(client=self.request.user).order_by('-uploaded_at')
