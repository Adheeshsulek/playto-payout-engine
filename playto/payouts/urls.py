from django.urls import path
from .views import balance_view, create_payout, seed_data

urlpatterns = [
    path('balance', balance_view),
    path('payouts', create_payout),
    path('seed/', seed_data),
]