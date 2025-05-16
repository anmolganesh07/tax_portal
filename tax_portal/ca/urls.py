from django.urls import path
from ca.views import CADashboardView, CAClientDetailView, FileReturnView

urlpatterns = [
    path('ca-dashboard/', CADashboardView.as_view(), name='ca_dashboard'),
    path('client/<int:pk>/', CAClientDetailView.as_view(), name='ca_client_detail'),
    path('file-return/', FileReturnView.as_view(), name='file_return'),
]
