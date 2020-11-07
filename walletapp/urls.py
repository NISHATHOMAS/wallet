from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path
from walletapp import views

urlpatterns = [
    path('', views.ManageWallet.as_view()),
    path('deposits/', views.Deposit.as_view()),
    path('withdrawals/', views.Withdraw.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
