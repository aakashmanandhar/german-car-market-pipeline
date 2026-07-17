from django.urls import path
from . import views

urlpatterns = [
    path('brand-market-share/', views.brand_market_share, name='brand-market-share'),
    path('kpi-summary/', views.kpi_summary, name='kpi-summary'),
    path('revenue-by-region/', views.revenue_by_region, name='revenue-by-region'),
    path('revenue-by-financing/', views.revenue_by_financing, name='revenue-by-financing'),
    path('channel-shift/', views.channel_shift, name='channel-shift'),
    path('fuel-type-trend/', views.fuel_type_trend, name='fuel-type-trend'),
    path('price-trend/', views.price_trend, name='price-trend'),
    path('new-vs-used/', views.new_vs_used, name='new-vs-used'),
    path('ask/', views.ask, name='ask'),
]