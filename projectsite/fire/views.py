from itertools import count
from typing import override
from django.db.models.fields import return_None
from django.shortcuts import render
from django.views.generic.list import ListView
from fire.models import Locations, Incident, FireStation
from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth
from django.db.models import Count
from datetime import datetime


class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"

class ChartView(ListView):
    model = Incident  # Add the model
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data needed for charts
        context['chart_data'] = True
        return context

    def get_queryset(self):
        return Incident.objects.all()  # Return actual queryset

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
        # Construct the dictionary with seerity level as keys and count as values
        data = {str(severity): int(count) for severity, count in rows}  # Ensure proper data types
    else:
        data = {"No Data": 100}  # Default data if no records found
        
    return JsonResponse(data)

def LineCountbyMonth(request):
    current_year = datetime.now().year

    result = {month: 0 for month in range(1, 13)}

    incidents_per_month = incident.object.filter(date_time_year=current_year) \
        .values_list('date_time', flat=True)

       # Counting the number of incidents per month
    for date_time in incidents_per_month:
        month = date_time.month
        result[month] += 1

    # If you want to convert month numbers to month names, youcan use a dictionary mapping
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }

    result_with_month_names = {month_names[month]: count for month, count in result.items()}

    return JsonResponse(result_with_month_names)


    
def map_station(request):
    fire_stations = FireStation.objects.values('name', 'latitude', 'longitude')

    for fs in fire_stations:
        fs['latitude'] = float(fs['latitude'])
        fs['longitude'] = float(fs['longitude'])

    context = {
        'fire_station': fire_stations,  
    }
    return render(request, 'map_station.html', context)


def monthly_incidents(request):
    current_year = datetime.now().year
    monthly_data = Incident.objects.filter(date__year=current_year)\
        .annotate(month=ExtractMonth('date'))\
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
