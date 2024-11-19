# main/views.py

import logging
from django.shortcuts import render


def index(request):
    return render(request, 'ALY_GTD/index.html')

def fleet_master(request):
    return render(request, 'ALY_GTD/fleet_master.html')

def commercial_master(request):
    return render(request, 'ALY_GTD/commercial_master.html')

def lookup_master(request):
    return render(request, 'ALY_GTD/lookup_master.html')

def traffic_master(request):
    return render(request, 'ALY_GTD/traffic_file_master.html')

def approver_dashboard(request):
    return render(request, 'ALY_GTD/approver_dashboard.html')


def email_template(request):
    return render(request, 'ALY_GTD/email_template.html')


def action_history(request):
    return render(request, 'ALY_GTD/action_history.html')


def traffic_action_history(request):
    return render(request, 'ALY_GTD/traffic_action_history.html')


logger = logging.getLogger(__name__)

def all_attachment(request):
    logger.info("all_attachment view called")
    print("all_attachment view called")
    return render(request, 'ALY_GTD/all_attachment.html')

def commercial_attachment(request):
    logger.info("commercial_attachment view called")
    print("commercial_attachment view called")
    return render(request, 'ALY_GTD/commercial_attachment.html')

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def your_view(request):
    pass



