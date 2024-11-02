# messaging/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import ChatMessage  # Assuming you have a ChatMessage model
from .serializers import ChatMessageSerializer  # You need to create a serializer

class ChatViewSet(viewsets.ViewSet):

    @action(detail=True, methods=['post'])
    def send_message(self, request, room_name):
        serializer = ChatMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(room_name=room_name)
            # Here you might want to send the message through the WebSocket channel
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def get_messages(self, request, room_name):
        messages = ChatMessage.objects.filter(room_name=room_name)
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

