import json
#import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.db.models import OuterRef, Subquery
from django.utils.dateparse import parse_datetime
from .models import Machine, MachineLocation

def machine_map(request):
    # 1. Subqueries to find the latest latitude, longitude, and timestamp for EACH machine
    latest_locs = MachineLocation.objects.filter(machine=OuterRef('pk')).order_by('-timestamp')
    
    latest_lat = latest_locs.values('latitude')[:1]
    latest_lng = latest_locs.values('longitude')[:1]
    latest_time = latest_locs.values('timestamp')[:1]
    
    # 2. Query machines and attach only their latest spatial data
    machines_with_location = Machine.objects.annotate(
        latest_latitude=Subquery(latest_lat),
        latest_longitude=Subquery(latest_lng),
        latest_timestamp=Subquery(latest_time)
    )
    
    # Filter out any machines that haven't sent a single GPS signal yet for the map pins
    active_locations = [
        m for m in machines_with_location 
        if m.latest_latitude is not None and m.latest_longitude is not None
    ]

    context = {
        'machines': machines_with_location,  # Keeps all machines in the sidebar list
        'active_locations': active_locations # Only the single latest point per machine for the map
    }
    return render(request, 'machinery/map.html', context)

def machines(request):
    latest_locs = MachineLocation.objects.filter(machine=OuterRef('pk')).order_by('-timestamp')
    
    latest_lat = latest_locs.values('latitude')[:1]
    latest_lng = latest_locs.values('longitude')[:1]
    latest_time = latest_locs.values('timestamp')[:1]
    
    # 2. Query machines and attach only their latest spatial data
    machines_with_location = Machine.objects.annotate(
        latest_latitude=Subquery(latest_lat),
        latest_longitude=Subquery(latest_lng),
        latest_timestamp=Subquery(latest_time)
    )

    active_locations = [
        m for m in machines_with_location
        if m.latest_latitude is not None and m.latest_longitude is not None
    ]

    return render(request, 'machinery/machines.html', {
        'machines': machines_with_location,
        'active_locations': active_locations
    })

def machine_detail(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    pings = MachineLocation.objects.filter(machine=machine).order_by('-timestamp')
    
    context = {
        'machine': machine,
        'pings': pings
    }
    return render(request, 'machinery/machine.html', context)

def agent(request):
    machines = Machine.objects.all().order_by('name')
    return render(request, 'machinery/agent.html', {'machines': machines})

@csrf_exempt
def save_agent_location(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
        
    try:
        data = json.loads(request.body)
        
        machine_id = data.get('machine_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        timestamp_raw = data.get('timestamp')

        # Validate that we have the required coordinates
        if not all([machine_id, latitude, longitude]):
            return JsonResponse({"status": "error", "message": "Missing core coordinates or asset identifiers."}, status=400)

        # Confirm the machine exists in the database
        try:
            machine_instance = Machine.objects.get(id=int(machine_id))
        except (Machine.DoesNotExist, ValueError):
            return JsonResponse({
                "status": "error", 
                "message": f"Asset verification failure: Machine ID {machine_id} does not exist."
            }, status=404)

        # Build the location record parameters
        db_record_args = {
            "machine": machine_instance,
            "latitude": latitude,
            "longitude": longitude
        }

        # Override default timestamp if a historical line came from the mobile frontend
        if timestamp_raw:
            parsed_time = parse_datetime(timestamp_raw)
            if parsed_time:
                db_record_args["timestamp"] = parsed_time

        # Save directly to the SQL Database table
        MachineLocation.objects.create(**db_record_args)
            
        return JsonResponse({
            "status": "success", 
            "message": "Telemetry populated to database registry seamlessly."
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Malformed JSON structure input."}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"System Ingestion Fault: {str(e)}"}, status=500)