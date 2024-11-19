# # main/urls.py

# from django.urls import path

# from Core import settings
# from . import views

# from django.conf.urls.static import static

# urlpatterns = [
#     path('', views.index, name='index'),
#     path('fleet_master/', views.fleet_master, name='fleet_master'),
    
# ]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


from django.conf import settings
from django.urls import path

# from ALY_GTD.api import api
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),  # Regular view URLs
    path('fleet_master/', views.fleet_master,name='fleet_master'),
    path('all-attachment/', views.all_attachment, name='all_attachment'),
    path('traffic_master/', views.traffic_master, name='traffic_master'), 
    path('lookup_master/', views.lookup_master, name='lookup_master'),
    path('commercial_master/', views.commercial_master, name='commercial_master'),  
    path('commercial-attachment/', views.commercial_attachment, name='commercial_attachment'), 
    path('approver_dashboard/',views.approver_dashboard,name='approver_dashboard'),
    path('action_history/', views.action_history, name='action_history'),
    path('email_template/',views.email_template,name='email_template'),
    path('traffic_action_history/', views.traffic_action_history, name='traffic_action_history'),
      # Regular view URLs

    
   # Include the Django Ninja API URLs
]
