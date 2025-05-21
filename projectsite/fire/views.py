from itertools import count
from django.db.models.fields import return_None
from django.shortcuts import render, redirect, get_object_or_404  # Add get_object_or_404 here
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from fire.models import Locations, Incident, FireStation, Firefighters, FireTruck, WeatherConditions
from django.db import connection
from django.http import JsonResponse
from datetime import datetime
from django.db.models import Count
from django.db.models.functions import ExtractMonth
import json
from .models import WeatherConditions
from django.contrib import messages


class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"

class ChartView(ListView):
    model = Incident
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data needed for charts
        context['chart_data'] = True
        return context

    def get_queryset(self):
        return Incident.objects.all()

def PieCountbySeverity(request):
    query = '''
    SELECT severity_level, COUNT(*) as count
    FROM fire_incident
    GROUP BY severity_level
    '''

    data = {}
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        
    if rows:
        # Construct the dictionary with severity level as keys and count as values
        data = {str(severity): int(count) for severity, count in rows}  # Ensure proper data types
    else:
        # Return test data that matches your reference image with 4 segments
        data = {
            "Low": 25,
            "Medium": 15,
            "High": 10,
            "Critical": 50
        }
        
    return JsonResponse(data, safe=False)

def LineCountbyMonth(request):
    current_year = datetime.now().year

    result = {month: 0 for month in range(1, 13)}

    incidents_per_month = Incident.objects.filter(date_time__year=current_year) \
        .values_list('date_time', flat=True)
    
    # Counting the number of incidents per month
    for date_time in incidents_per_month:
        month = date_time.month
        result[month] += 1
    
    # If you want to convert month numbers to month names, you can use a dictionary mapping
    month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                  7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    
    result_with_month_names = {
        month_names[int(month)]: count for month, count in result.items()
    }
    
    return JsonResponse(result_with_month_names)


def map_station(request):
    fire_stations = FireStation.objects.all()
    station_list = []
    
    for station in fire_stations:
        station_list.append({
            'name': station.name,
            'latitude': float(station.latitude) if station.latitude else 0,
            'longitude': float(station.longitude) if station.longitude else 0,
            'address': station.address,
            'city': station.city,
            'country': station.country
        })
    
    # Check if a specific component is requested
    path = request.path.split('/')
    if len(path) > 3 and 'components' in path:
        # Get the component name (remove .html extension if present)
        component_index = path.index('components') + 1
        if component_index < len(path):
            component = path[component_index].split('.')[0]  # Remove .html extension
            
            # Handle specific components
            if component == 'base':
                return render(request, 'components/base.html')
            elif component == 'locations':
                return render(request, 'crud/locations/list.html', {'locations': Locations.objects.all(), 'title': 'Locations'})
            elif component == 'incident':
                return render(request, 'crud/incidents/list.html', {'incidents': Incident.objects.all(), 'title': 'Incidents'})
            elif component == 'fire-station':
                return render(request, 'crud/stations/list.html', {'stations': FireStation.objects.all(), 'title': 'Fire Stations'})
            elif component == 'fire-fighter':
                return render(request, 'crud/firefighters/list.html', {'firefighters': Firefighters.objects.all(), 'title': 'Fire Fighters'})
            elif component == 'fire-truck':
                return render(request, 'crud/firetrucks/list.html', {'firetrucks': FireTruck.objects.all(), 'title': 'Fire Trucks'})
            elif component == 'weather-condition':
                return render(request, 'crud/weather/list.html', {'weather_conditions': WeatherConditions.objects.all(), 'title': 'Weather Conditions'})
            else:
                return render(request, f'components/{component}.html', {'stations': json.dumps(station_list)})
    
    return render(request, 'maps/map_station.html', {'stations': json.dumps(station_list)})


def monthly_incidents(request):
    current_year = datetime.now().year
    monthly_data = Incident.objects.filter(date_time__year=current_year)\
        .annotate(month=ExtractMonth('date_time'))\
        .values('month')\
        .annotate(count=Count('id'))\
        .order_by('month')

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    data = {
        'labels': months,
        'values': [0] * 12  # Initialize with zeros
    }
    
    for item in monthly_data:
        month_index = item['month'] - 1  # Convert 1-based to 0-based index
        data['values'][month_index] = item['count']
    
    return JsonResponse(data)


def map_incident(request):
    incidents = Incident.objects.select_related('location').values(
        'location__name',
        'severity_level', 
        'date_time',
        'description', 
        'location__latitude',
        'location__longitude'
    ).order_by('-date_time')
    
    incidents_list = []
    for incident in incidents:
        if incident['location__latitude'] and incident['location__longitude']:
            incident_dict = {
                'location': incident['location__name'],
                'severity_level': incident['severity_level'],
                'date': incident['date_time'].strftime('%Y-%m-%d') if incident['date_time'] else '',
                'description': incident['description'],
                'latitude': float(incident['location__latitude']),
                'longitude': float(incident['location__longitude'])
            }
            incidents_list.append(incident_dict)

    context = {
        'incidents': json.dumps(incidents_list),
        'title': 'Fire Incidents Map'
    }
    return render(request, 'maps/map_incident.html', context)


def FireCountBySeverity(request):
    query = """
    SELECT severity_level, COUNT(*) as count
    FROM fire_incident
    GROUP BY severity_level
    """
    data = {}
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        
    if rows:
        # Construct the dictionary with severity level as keys and count as values
        data = {severity: count for severity, count in rows}
    else:
        data = {}
        
    return JsonResponse(data)


def MultilineIncidentTopCountry(request):
    query = '''
    SELECT 
        l.country,
        strftime('%m', i.date_time) AS month,
        COUNT(i.id) AS incident_count
    FROM 
        fire_incident i
    JOIN 
        fire_locations l ON l.id = i.location_id
    WHERE 
        l.country IN (
            SELECT 
                l_top.country
            FROM 
                fire_incident i_top
            JOIN 
                fire_locations l_top ON l_top.id = i_top.location_id
            WHERE 
                strftime('%Y', i_top.date_time) = strftime('%Y', 'now')
            GROUP BY 
                l_top.country
            ORDER BY 
                COUNT(i_top.id) DESC
            LIMIT 3
        )
        AND strftime('%Y', i.date_time) = strftime('%Y', 'now')
    GROUP BY 
        l.country, month
    ORDER BY 
        l.country, month;
    '''
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    
    # Initialize a dictionary to store the result
    result = {}
    
    # Initialize a set of months from January to December
    months = set(str(i).zfill(2) for i in range(1, 13))
    
    # Loop through the query results
    for row in rows:
        country = row[0]
        month = row[1]
        total_incidents = row[2]
        
        # If the country is not in the result dictionary, initialize it with all months set to zero
        if country not in result:
            result[country] = {month: 0 for month in months}
        
        # Update the incident count for the corresponding month
        result[country][month] = total_incidents
    
    # Ensure there are always 3 countries in the result
    while len(result) < 3:
        missing_country = f"Country {len(result) + 1}"
        result[missing_country] = {month: 0 for month in months}
    
    for country in result:
        result[country] = dict(sorted(result[country].items()))
    
    return JsonResponse(result)


def MultipleBarbySeverity(request):
    # Get the current year
    current_year = datetime.now().year
    
    # SQL query to get incident counts by severity level and month
    query = '''
    SELECT 
        severity_level,
        strftime('%m', date_time) AS month,
        COUNT(*) as count
    FROM 
        fire_incident
    WHERE 
        strftime('%Y', date_time) = strftime('%Y', 'now')
    GROUP BY 
        severity_level, month
    ORDER BY 
        severity_level, month
    '''
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    
    # Initialize a dictionary to store results by severity level
    result = {}
    
    # Initialize a set of months from January to December
    months = set(str(i).zfill(2) for i in range(1, 13))
    
    # Process the query results
    for row in rows:
        severity = row[0]
        month = row[1]
        count = row[2]
        
        # If the severity level is not in the result dictionary, initialize it
        if severity not in result:
            result[severity] = {month: 0 for month in months}
        
        # Update the count for the corresponding month
        result[severity][month] = count
    
    # If no data was found, provide sample data for visualization
    if not result:
        severity_levels = ['Minor Fire', 'Moderate Fire', 'Major Fire']
        for severity in severity_levels:
            result[severity] = {month: 0 for month in months}
            # Add some random data for testing
            for month in months:
                result[severity][month] = 0
    
    # Ensure the months are sorted correctly for each severity level
    for severity in result:
        result[severity] = dict(sorted(result[severity].items()))
    
    return JsonResponse(result)


# CRUD Views for Locations
class LocationListView(ListView):
    model = Locations
    template_name = 'crud/locations/list.html'
    context_object_name = 'locations'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Locations List'
        return context
    
    

class LocationCreateView(CreateView):
    model = Locations
    template_name = 'crud/locations/form.html'
    fields = ['name', 'address', 'city', 'country', 'latitude', 'longitude']
    success_url = '/locations/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Location'
        return context
    
    def form_valid(self, form):
        reponse = super().form_valid(form)
        messages.success(self.request, 'Location added successfully.')
        return reponse

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error adding the location.')
        return super().form_invalid(form)

        

class LocationUpdateView(UpdateView):
    model = Locations
    template_name = 'crud/locations/form.html'
    fields = ['name', 'address', 'city', 'country', 'latitude', 'longitude']
    success_url = '/locations/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Location: {self.object.name}'
        return context

    def form_valid(self, form):
        reponse = super().form_valid(form)
        messages.success(self.request, 'Location updated successfully.')
        return reponse

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error updating the location.')
        return super().form_invalid(form)

class LocationDeleteView(DeleteView):
    model = Locations
    template_name = 'crud/locations/delete.html'
    success_url = '/locations/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete Location: {self.object.name}'
        return context
    
        
    
# CRUD Views for Incidents
class IncidentListView(ListView):
    model = Incident
    template_name = 'crud/incidents/list.html'
    context_object_name = 'incidents'
    ordering = ['-date_time']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Fire Incidents List'
        return context

class IncidentCreateView(CreateView):
    model = Incident
    template_name = 'crud/incidents/form.html'
    fields = ['location', 'severity_level', 'date_time', 'description']
    success_url = '/incidents/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Report New Fire Incident'
        context['locations'] = Locations.objects.all()
        return context
    
    def form_valid(self, form):
        reponse = super().form_valid(form)
        messages.success(self.request, 'Incident added successfully.')
        return reponse

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error adding the incident.')
        return super().form_invalid(form)


class IncidentUpdateView(UpdateView):
    model = Incident
    template_name = 'crud/incidents/form.html'
    fields = ['location', 'severity_level', 'date_time', 'description']
    success_url = '/incidents/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Incident: {self.object.id}'
        context['locations'] = Locations.objects.all()
        return context

    def form_valid(self, form):
        reponse = super().form_valid(form)
        messages.success(self.request, 'Incident updated successfully.')
        return reponse

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error updating the incident.')
        return super().form_invalid(form)

class IncidentDeleteView(DeleteView):
    model = Incident
    template_name = 'crud/incidents/delete.html'
    success_url = '/incidents/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete Incident: {self.object.id}'

# CRUD Views for Fire Stations
class StationListView(ListView):
    model = FireStation
    template_name = 'crud/stations/list.html'
    context_object_name = 'stations'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Fire Stations List'
        return context

class StationCreateView(CreateView):
    model = FireStation
    template_name = 'crud/stations/form.html'
    fields = ['name', 'address', 'city', 'country']
    success_url = '/stations/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Fire Station'
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Station added successfully.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error adding the station.')
        return super().form_invalid(form)

class StationUpdateView(UpdateView):
    model = FireStation
    template_name = 'crud/stations/form.html'
    fields = ['name', 'address', 'city', 'country']
    success_url = '/stations/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Fire Station: {self.object.name}'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Station updated successfully.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error updating the station.')
        return super().form_invalid(form)

class StationDeleteView(DeleteView):
    model = FireStation
    template_name = 'crud/stations/delete.html'
    success_url = '/stations/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete Fire Station: {self.object.name}'

# CRUD Views for Fire Fighters
class FirefighterListView(ListView):
    model = Firefighters
    template_name = 'crud/firefighters/list.html'
    context_object_name = 'firefighters'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Fire Fighters List'
        return context

class FirefighterCreateView(CreateView):
    model = Firefighters
    template_name = 'crud/firefighters/form.html'
    fields = ['name', 'badge_number', 'rank', 'station', 'phone', 'experience_level']
    success_url = '/firefighters/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Fire Fighter'
        context['stations'] = FireStation.objects.all()
        return context

    def form_valid(self, form):
        reponse = super().form_valid(form)
        messages.success(self.request, 'Firefighter added successfully.')
        return reponse

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error adding the firefighter.')
        return super().form_invalid(form)

class FirefighterUpdateView(UpdateView):
    model = Firefighters
    template_name = 'crud/firefighters/form.html'
    fields = ['name', 'badge_number', 'rank', 'station', 'phone', 'email']
    success_url = '/firefighters/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Fire Fighter: {self.object.name}'
        context['stations'] = FireStation.objects.all()
        return context
    
    def form_valid(self, form):
        reponse = super().form_valid(form)
        messages.success(self.request, 'Firefighter updated successfully.')
        return reponse

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error updating the firefighter.')
        return super().form_invalid(form)

class FirefighterDeleteView(DeleteView):
    model = Firefighters
    template_name = 'crud/firefighters/delete.html'
    success_url = '/firefighters/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete Fire Fighter: {self.object.name}'
        return context

# CRUD Views for Fire Trucks
class FireTruckListView(ListView):
    model = FireTruck
    template_name = 'crud/firetrucks/list.html'
    context_object_name = 'firetrucks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Fire Trucks List'
        return context

class FireTruckCreateView(CreateView):
    model = FireTruck
    template_name = 'crud/firetrucks/form.html'
    fields = ['truck_number', 'model', 'capacity', 'station']
    success_url = '/firetrucks/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Fire Truck'
        context['stations'] = FireStation.objects.all()  # Add stations to context
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Fire truck added successfully.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error adding the fire truck.')
        return super().form_invalid(form)

class FireTruckUpdateView(UpdateView):
    model = FireTruck
    template_name = 'crud/firetrucks/form.html'
    fields = ['truck_number', 'model', 'capacity', 'station']
    success_url = '/firetrucks/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Fire Truck: {self.object.truck_number}'
        context['stations'] = FireStation.objects.all()  # Add stations to context
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Fire truck updated successfully.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error updating the fire truck.')
        return super().form_invalid(form)

class FireTruckDeleteView(DeleteView):
    model = FireTruck
    template_name = 'crud/firetrucks/delete.html'
    success_url = '/firetrucks/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete Fire Truck: {self.object.vehicle_number}'
        return context

# CRUD Views for Weather Conditions
class WeatherConditionListView(ListView):
    model = WeatherConditions
    template_name = 'crud/weather/list.html'
    context_object_name = 'weather_data'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Weather Conditions List'
        return context

class WeatherConditionCreateView(CreateView):
    model = WeatherConditions
    template_name = 'crud/weather/form.html'
    fields = ['date', 'incident', 'temperature', 'humidity', 'wind_speed', 'weather_description']
    success_url = '/weather/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Weather Data'
        context['incidents'] = Incident.objects.all()
        context['stations'] = FireStation.objects.all()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Weather data added successfully.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error adding weather data.')
        return super().form_invalid(form)

class WeatherConditionUpdateView(UpdateView):
    model = WeatherConditions
    template_name = 'crud/weather/form.html'
    fields = ['date', 'incident', 'temperature', 'humidity', 'wind_speed', 'weather_description']
    success_url = '/weather/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Weather Data: {self.object.id}'
        context['incidents'] = Incident.objects.all()
        context['stations'] = FireStation.objects.all()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Weather data updated successfully.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error updating weather data.')
        return super().form_invalid(form)

class WeatherConditionDeleteView(DeleteView):
    model = WeatherConditions
    template_name = 'crud/weather/delete.html'
    success_url = '/weather/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete Weather Data: {self.object.id}'
        return context


def add_firefighter(request):
    stations = FireStation.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        rank = request.POST.get('rank')
        experience_level = request.POST.get('experience_level')
        station_id = request.POST.get('station')
        contact_info = request.POST.get('contact_info')
        station = FireStation.objects.get(id=station_id)
        firefighter = Firefighters.objects.create(
            name=name,
            rank=rank,
            experience_level=experience_level,
            station=station,
            phone=contact_info  # or map to the correct field
        )
        return redirect('firefighter_list')
    return render(request, 'crud/firefighters/form.html', {'stations': stations})

