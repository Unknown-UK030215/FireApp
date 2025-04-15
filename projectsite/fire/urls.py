from django.contrib import admin
from django.urls import path

from fire.views import HomePageView, ChartView, PieCountbySeverity, LineCountbyMonth
from fire import views
from fire.views import monthly_incidents

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.HomePageView.as_view(), name='home'),
    path('stations/', views.map_station, name='map-station'),
    path('dashboard_chart/', views.ChartView.as_view(), name='dashboard-chart'),
    path('chart/', views.PieCountbySeverity, name='chart'),
    path('monthly-incidents/', views.monthly_incidents, name='monthly-incidents'),
    path('maps/fire-incidents/', views.map_incident, name='fire_incidents_map'),  # Add this line
]