import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import OuterRef, Subquery, Count
from django.utils.dateparse import parse_datetime
from datetime import timedelta
from django.utils import timezone
from .models import Machine, MachineLocation, Team, Agent, Member
import uuid

def home(request):
    num_machines = Machine.objects.count()
    num_transmitting = Agent.objects.filter(
        is_transmitting=True
    ).count()

    cutoff = timezone.now() - timedelta(hours=24)
    num_pings24 = MachineLocation.objects.filter(
        timestamp__gte=cutoff
    ).count()

    return render(request, "machinery/home.html", {
        "num_machines": num_machines,
        "num_transmitting": num_transmitting,
        "num_pings24": num_pings24,
    })

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

def machine_edit(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    if request.method == 'POST':
        # Handle form submission
        machine.name = request.POST.get('name') or machine.name
        machine.serial_number = request.POST.get('serial_number') or machine.serial_number
        machine.save()
        return redirect('machine_detail', pk=machine.pk)
    return render(request, 'machinery/machine_edit.html', {'machine': machine})

def machine_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        serial_number = request.POST.get('serial_number')
        if name and serial_number:
            machine = Machine.objects.create(name=name, serial_number=serial_number)
            return redirect('machine_detail', pk=machine.pk)
    return render(request, 'machinery/machine_add.html')

def machine_delete(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    if request.method == 'POST':
        machine.delete()
        return redirect('machines')
    return redirect('machines')


def agent(request):
    agent_uid = request.session.get('agent_uid')
    if not agent_uid:
        return redirect('home') # Or show an error that they aren't registered
        
    try:
        current_agent = Agent.objects.get(uid=agent_uid)
    except Agent.DoesNotExist:
        return redirect('home')
        
    # Render your telemetry transmission page...
    return render(request, 'machinery/agent.html', {'agent': current_agent})


def agent_register(request, machine_id):
    machine = get_object_or_404(Machine, pk=machine_id)
    
    if request.method == 'POST':
        cell_number = request.POST.get('cell_number')
        
        if not cell_number:
            return HttpResponseBadRequest("Cell number is required.")
            
        # Find the member by cell number
        try:
            member = Member.objects.get(cell_number=cell_number)
        except Member.DoesNotExist:
            return render(request, 'machinery/agent_register.html', {
                'machine': machine,
                'error': 'Member not found. Please check your cell number.'
            })
            
        # Generate a unique UID for this device
        device_uid = str(uuid.uuid4())
        
        # Create the new Agent record
        agent = Agent.objects.create(
            member=member,
            machine=machine,
            uid=device_uid,
            is_transmitting=False
        )
        
        # Store the UID in the session so the telemetry page knows who is transmitting
        request.session['agent_uid'] = device_uid
        
        # Redirect to the page that handles telemetry
        return redirect('agent')
        
    return render(request, 'machinery/agent_register.html', {'machine': machine})

@csrf_exempt
def set_agent_transmit(request):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=405)
    data = json.loads(request.body)
    is_transmitting = data.get("is_transmitting", False)
    # 1. Get the specific device's UID from the session
    agent_uid = request.session.get('agent_uid')
    if not agent_uid:
        return JsonResponse({"status": "error", "message": "No active agent session."}, status=401)
    # 2. Look up the Agent by its unique UID
    try:
        agent = Agent.objects.get(uid=agent_uid)
        agent.is_transmitting = bool(is_transmitting)
        agent.save(update_fields=["is_transmitting"])
        return JsonResponse({"status": "success"})
    except Agent.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Agent not found."}, status=404)

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

def teams(request):
    teams = Team.objects.annotate(
        num_members=Count('member')
    ).order_by('name')

    return render(request,'machinery/teams.html', {
        'teams': teams,
    })

def agents(request):
    agents = Agent.objects.all().order_by('member')
    return render(request, 'machinery/agents.html', {'agents': agents})

def agent_add(request):
    if request.method == 'POST':
        member = request.POST.get('member')
        machine_id = request.POST.get('machine_id')
        if member and machine_id:
            machine = get_object_or_404(Machine, pk=machine_id)
            Agent.objects.create(member=member, machine=machine)
            return redirect('agents')
    machines = Machine.objects.all()
    return render(request, 'machinery/agent_add.html', {'machines': machines})
    