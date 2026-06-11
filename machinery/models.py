from django.db import models
from django.utils import timezone # Add this import

class Member(models.Model):
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    cell_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.fname} {self.lname}"

class Team(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class Machine(models.Model):
    name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=50, unique=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class MachineLocation(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.machine.name} at {self.timestamp}"