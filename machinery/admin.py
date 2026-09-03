from django.contrib import admin
from .models import Machine, MachineLocation, Team, Member, Agent

admin.site.register(Machine)
admin.site.register(MachineLocation)
admin.site.register(Team)
admin.site.register(Member)
admin.site.register(Agent)
