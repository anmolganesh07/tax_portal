from dashboard.views import itr_home_view
from django.urls import path


urlpatterns = [
    path('itr_home/', itr_home_view, name='itr_home'),
]
