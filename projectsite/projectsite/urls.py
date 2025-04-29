from django.contrib import admin
from django.urls import path, include
from fire.views import (
    HomePageView,
    ChartView,
    FireCountBySeverity,
    LineCountbyMonth,
    MultilineIncidentTopCountry,
    MultipleBarbySeverity
)
from fire import views  # Add this import to access the views module directly

urlpatterns = [
    # Admin interface
    path("admin/", admin.site.urls),

    # Main pages
    path('', HomePageView.as_view(), name='home'),
    path('dashboard_chart/', ChartView.as_view(), name='dashboard-chart'),

    # Chart endpoints
    path('severity/', FireCountBySeverity, name='chart'),
    path('linechart/', LineCountbyMonth, name='linechart'),
    path('multilinechart/', MultilineIncidentTopCountry, name='chart'),
    path('multibarchart/', MultipleBarbySeverity, name='chart'),
    
    # Map related endpoints
    path('maps/', include([
        path('fire-incidents/', views.map_incident, name='fire_incidents_map'),
        path('stations/', views.map_station, name='map-station'),
    ])),
]