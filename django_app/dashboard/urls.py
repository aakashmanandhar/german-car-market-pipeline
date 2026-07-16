from django.urls import path
from . import views

urlpatterns = [
    path('brand-market-share/', views.brand_market_share, name='brand-market-share'),
]