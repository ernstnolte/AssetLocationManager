from django.urls import path
from . import views

urlpatterns = [
    path('map/', views.machine_map, name='machine_map'),
    path('machine/<int:pk>/', views.machine_detail, name='machine_detail'),
    path('agent/', views.agent, name='agent'),
    path('agent/save/', views.save_agent_location, name='save_agent_location'),
]