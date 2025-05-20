from django.urls import path
from .views import TDSCalculatorView, DownloadReportView, DueDateTrackerView


urlpatterns = [
    path('', TDSCalculatorView.as_view(), name='tds_calculator'),
    path('download/', DownloadReportView.as_view(), name='download_report'),
    path('due-dates/', DueDateTrackerView.as_view(), name='due_dates'),
]
