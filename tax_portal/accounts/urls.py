from django.urls import path
from .views import (
    ClientSignUpView, CASignUpView, CustomLoginView, CustomLogoutView,
    ItrUserSignUpView, ItrUserLoginView, ClientPersonalInfoView, ItrPersonalInfoView,
    SelfDeclarationView, AcknowledgmentView,
)
from django.views.generic import TemplateView

urlpatterns = [
    path('signup/client/', ClientSignUpView.as_view(), name='client_signup'),
    path('signup/ca/', CASignUpView.as_view(), name='ca_signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('signup/itr/', ItrUserSignUpView.as_view(), name='itr_signup'),
    path('login/itr/', ItrUserLoginView.as_view(), name='login_itr'),
    path('itr/personal-info/', ItrPersonalInfoView.as_view(), name='itr_personal_info'),
    path('client/personal-info/', ClientPersonalInfoView.as_view(), name='client_personal_info'),
    path('self-declaration/', SelfDeclarationView.as_view(), name='self_declaration'),
    path('acknowledgment/', AcknowledgmentView.as_view(), name='acknowledgment'),
]
