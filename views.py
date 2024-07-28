# messaging/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def voice_messaging_view(request):
    username = request.user.username  # Get the authenticated user's username
    return render(request, 'voice_messaging.html', {'username': username})

