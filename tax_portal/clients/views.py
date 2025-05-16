from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Document, ReturnFiling
from .forms import DocumentUploadForm
from django.utils import timezone
from datetime import date

class ClientDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'clients/dashboard.html'

    def test_func(self):
        return self.request.user.role == 'client'  # Only allow Clients
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        start_date = date(2025, 5, 1)
        end_date = date(2025, 7, 31)

        returns = ReturnFiling.objects.filter(
            client=self.request.user,
            due_date__gte=start_date,
            due_date__lte=end_date
        ).order_by('due_date')

        context['returns'] = returns
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
    template_name = 'clients/document_list.html'  # create this template next
    context_object_name = 'documents'
    paginate_by = 10  # Optional: paginate if many docs

    def test_func(self):
        return self.request.user.role == 'client'

    def get_queryset(self):
        return Document.objects.filter(client=self.request.user).order_by('-uploaded_at')
    