from django.db import models
from django.utils import timezone # Add this import

class Machine(models.Model):
    name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class MachineLocation(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    # Changed here: Now it uses server time by default, but lets us override it manually
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.machine.name} at {self.timestamp}"