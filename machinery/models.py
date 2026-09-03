from django.db import models
from django.utils import timezone

class Team(models.Model):
    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name

class Member(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    cell_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.fname} {self.lname}"

class Machine(models.Model):
    name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=50, unique=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class Agent(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=False)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, null=False)
    uid = models.CharField(unique=True, max_length=50)

    def __str__(self):
        return self.uid

class MachineLocation(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.machine.name} at {self.timestamp}"