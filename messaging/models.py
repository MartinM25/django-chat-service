from django.db import models
from django.contrib.auth.models import User

class Chat(models.Model):
    participants = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat between {', '.join([user.username for user in self.participants.all()])}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('sent', 'Sent'), ('received', 'Received'), ('read', 'Read')])

    def __str__(self):
        return f"{self.sender.username}: {self.content} at {self.timestamp}"
