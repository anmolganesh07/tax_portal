from django.urls import path
from .views import ClientDashboardView, DocumentUploadView, ClientDocumentListView, ClientAcknowledgmentView

urlpatterns = [
    path('dashboard/', ClientDashboardView.as_view(), name='client_dashboard'),
    path('upload/', DocumentUploadView.as_view(), name='upload_document'),
    path('documents/', ClientDocumentListView.as_view(), name='client_documents'),
    path('acknowledgment/', ClientAcknowledgmentView.as_view(), name='client_acknowledgment'),
]
