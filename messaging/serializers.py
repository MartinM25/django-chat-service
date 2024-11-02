# messaging/serializers.py
from rest_framework import serializers
from .models import ChatMessage  # Your ChatMessage model

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'room_name', 'sender', 'message', 'timestamp']
