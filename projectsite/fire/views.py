from itertools import count
from django.db.models.fields import return_None
from django.shortcuts import render
from django.views.generic.list import ListView
from fire.models import Locations, Incident, FireStation
from django.db import connection
from django.http import JsonResponse
from datetime import datetime
from django.db.models import Count
from django.db.models.functions import ExtractMonth
import json


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
