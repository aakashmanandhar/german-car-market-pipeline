from django.urls import path
from . import views

urlpatterns = [
    path('brand-market-share/', views.brand_market_share, name='brand-market-share'),
    path('kpi-summary/', views.kpi_summary, name='kpi-summary'),
    path('revenue-by-region/', views.revenue_by_region, name='revenue-by-region'),
]