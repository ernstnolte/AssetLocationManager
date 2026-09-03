from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('map/', views.machine_map, name='machine_map'),
    path('machine/<int:pk>/', views.machine_detail, name='machine_detail'),
    path('machines/', views.machines, name='machines'),
    path('machine/<int:pk>/edit/', views.machine_edit, name='machine_edit'),
    path('machine/add/', views.machine_add, name='machine_add'),
    path('machine/edit/', views.machine_edit, name='machine_edit'),
    path('machine/<int:pk>/delete/', views.machine_delete, name='machine_delete'),
    path('agent/', views.agent, name='agent'),
    path('agent/save/', views.save_agent_location, name='save_agent_location'),
    path('agent/set_transmit/', views.set_agent_transmit, name='set_agent_transmit'),
    path('teams/', views.teams, name='teams'),
]