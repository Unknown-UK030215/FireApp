from django.contrib import admin
from django.urls import path, include
from fire.views import HomePageView, ChartView, PieCountbySeverity, LineCountbyMonth
from fire import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard_chart', ChartView.as_view(), name='dashboard-chart'),
    path('chart/', PieCountbySeverity, name='chart'),
    path('monthly-incidents/', views.monthly_incidents, name='monthly-incidents'),
    path('maps/', include([
        path('fire-incidents/', views.map_incident, name='fire_incidents_map'),
        path('stations/', views.map_station, name='map-station'),
    ])),
]
