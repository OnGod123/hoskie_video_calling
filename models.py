# models.py
from django.db import models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
    video_message = models.TextField(null=True, blank=True)  # Field for the video message (SDP offer/answer)
    ice_candidate = models.TextField(null=True, blank=True)  # Field for ICE candidates
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.video_message:
            return f'{self.sender} to {self.recipient}: Video Message'
        return f'{self.sender} to {self.recipient}: ICE Candidate'

