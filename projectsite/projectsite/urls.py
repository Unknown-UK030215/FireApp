from django.contrib import admin
from django.urls import path

from fire.views import HomePageView, ChartView, PieCountbySeverity, LineCountbyMonth
from fire import views
from fire.views import monthly_incidents
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('fire.urls')),
    path('stations', views.map_station, name='map-station'),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard_chart', ChartView.as_view(), name='dashboard-chart'),
    path('chart/', PieCountbySeverity, name='chart'),
    path('monthly-incidents/', monthly_incidents, name='monthly-incidents'),
    path('fire-incidents/map/', views.map_incident, name='fire_incidents_map'),
]
