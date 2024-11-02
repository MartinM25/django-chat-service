from django.db import models

class Message(models.Model):
    sender = models.CharField(max_length=255)  # Could be a ForeignKey to a User model
    recipient = models.CharField(max_length=255)  # Could also be a ForeignKey to a User model
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} to {self.recipient}: {self.content[:20]} at {self.timestamp}"
