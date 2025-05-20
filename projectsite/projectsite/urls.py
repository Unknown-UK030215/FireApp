from django.contrib import admin
from django.urls import path
from fire.views import (
    HomePageView, ChartView, PieCountbySeverity, LineCountbyMonth,
    map_station, monthly_incidents, map_incident, FireCountBySeverity,
    MultilineIncidentTopCountry, MultipleBarbySeverity,
    # Location views
    LocationListView, LocationCreateView, LocationUpdateView, LocationDeleteView,
    # Incident views
    IncidentListView, IncidentCreateView, IncidentUpdateView, IncidentDeleteView,
    # Station views
    StationListView, StationCreateView, StationUpdateView, StationDeleteView,
    # Firefighter views
    FirefighterListView, FirefighterCreateView, FirefighterUpdateView, FirefighterDeleteView,
    # Weather views
    WeatherConditionListView, WeatherConditionCreateView, WeatherConditionUpdateView, WeatherConditionDeleteView,
    # FireTruck views
    FireTruckListView, FireTruckCreateView, FireTruckUpdateView, FireTruckDeleteView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('chart/', ChartView.as_view(), name='chart'),
    path('pie-count-by-severity/', PieCountbySeverity, name='pie_count_by_severity'),
    path('line-count-by-month/', LineCountbyMonth, name='line_count_by_month'),
    path('map-station/', map_station, name='map_station'),
    path('monthly-incidents/', monthly_incidents, name='monthly_incidents'),
    path('map-incident/', map_incident, name='map_incident'),
    path('fire-count-by-severity/', FireCountBySeverity, name='fire_count_by_severity'),
    path('multiline-incident-top-country/', MultilineIncidentTopCountry, name='multiline_incident_top_country'),
    path('multiple-bar-by-severity/', MultipleBarbySeverity, name='multiple_bar_by_severity'),
    
    # Location URLs
    path('locations/', LocationListView.as_view(), name='location_list'),
    path('locations/create/', LocationCreateView.as_view(), name='location_create'),
    path('locations/<int:pk>/update/', LocationUpdateView.as_view(), name='location_update'),
    path('locations/<int:pk>/delete/', LocationDeleteView.as_view(), name='location_delete'),
    
    # Incident URLs
    path('incidents/', IncidentListView.as_view(), name='incident_list'),
    path('incidents/create/', IncidentCreateView.as_view(), name='incident_create'),
    path('incidents/<int:pk>/update/', IncidentUpdateView.as_view(), name='incident_update'),
    path('incidents/<int:pk>/delete/', IncidentDeleteView.as_view(), name='incident_delete'),
    
    # Station URLs
    path('stations/', StationListView.as_view(), name='station_list'),
    path('stations/create/', StationCreateView.as_view(), name='station_create'),
    path('stations/<int:pk>/update/', StationUpdateView.as_view(), name='station_update'),
    path('stations/<int:pk>/delete/', StationDeleteView.as_view(), name='station_delete'),
    
    # Firefighter URLs
    path('firefighters/', FirefighterListView.as_view(), name='firefighter_list'),
    path('firefighters/create/', FirefighterCreateView.as_view(), name='firefighter_create'),
    path('firefighters/<int:pk>/update/', FirefighterUpdateView.as_view(), name='firefighter_update'),
    path('firefighters/<int:pk>/delete/', FirefighterDeleteView.as_view(), name='firefighter_delete'),
    
    # FireTruck URLs
    path('firetrucks/', FireTruckListView.as_view(), name='firetruck_list'),
    path('firetrucks/create/', FireTruckCreateView.as_view(), name='firetruck_create'),
    path('firetrucks/<int:pk>/update/', FireTruckUpdateView.as_view(), name='firetruck_update'),
    path('firetrucks/<int:pk>/delete/', FireTruckDeleteView.as_view(), name='firetruck_delete'),
    
    # Weather Condition URLs
    path('weather/', WeatherConditionListView.as_view(), name='weather_list'),
    path('weather/create/', WeatherConditionCreateView.as_view(), name='weather_create'),
    path('weather/<int:pk>/update/', WeatherConditionUpdateView.as_view(), name='weather_update'),
    path('weather/<int:pk>/delete/', WeatherConditionDeleteView.as_view(), name='weather_delete'),
]