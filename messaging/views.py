import datetime

from asgiref.sync import async_to_sync
from bson import ObjectId
from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed
from channels.layers import get_channel_layer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from messaging.utils import decode_jwt
from pymongo import MongoClient
import os
import uuid 
from dotenv import load_dotenv

# Load environment variables and set up MongoDB client
load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client[os.getenv('MONGODB_NAME', 'test')]

class ChatViewSet(viewsets.ViewSet):
    
    @action(detail=False, methods=['post'])
    def create(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"error": "Authorization header missing or malformed"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]
        try:
            decoded = decode_jwt(token)
        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        participants = request.data.get('participants')
        if not participants or len(participants) != 1:
            return Response({"error": "At least two participants are required."}, status=status.HTTP_400_BAD_REQUEST)

        creator_id = decoded['user_id']
        unique_participants = [creator_id] + participants

        # Create a new chat document
        chat_data = {
            'participants': unique_participants,
            'created_at': datetime.datetime.now(),
            'creator': creator_id
        }

        try:
            result = db.chats.insert_one(chat_data)  # Insert into MongoDB
        except Exception as e:
            return Response({"error": "Database insertion failed", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "chat_id": str(result.inserted_id),
            "participants": unique_participants
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def send_message(self, request, chat_id):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"error": "Authorization header missing or malformed"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]
        try:
            decoded = decode_jwt(token)
        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        sender_id = decoded['user_id']
        content = request.data.get('content')

        if not content:
            return Response({"error": "Message content is required."}, status=status.HTTP_400_BAD_REQUEST)

        chat = db.chats.find_one({"_id": ObjectId(chat_id)})
        if not chat:
            return Response({"error": "Chat not found."}, status=status.HTTP_404_NOT_FOUND)

        message_data = {
            'chat_id': chat_id,
            'sender': sender_id,
            'content': content,
            'timestamp': datetime.datetime.now(),
        }

        try:
            result = db.messages.insert_one(message_data)
            message_data['_id'] = str(result.inserted_id)

            return Response(message_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": "Database insertion failed", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def get_messages(self, request, room_name):
        messages = list(db.messages.find({'room_name': room_name}))
        
        for message in messages:
            message['_id'] = str(message['_id'])
        
        return Response(messages, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='user-chats')
    def get_user_chats(self, request):

        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"error": "Authorization header missing or malformed"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]
        try:
            decoded = decode_jwt(token)
        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = decoded['user_id']
        
        # Find all chats where the user is a participant
        chats = list(db.chats.find({'participants': user_id}))
        
        chat_previews = []
        for chat in chats:
            participants = chat['participants']

            other_participant = [p for p in participants if str(p) != str(user_id)]
            
            last_message = db.messages.find({'room_name': chat['room_name']}).sort('timestamp', -1).limit(1)
            last_message_content = next(last_message, {}).get('content', 'No messages yet')
            
            chat_preview = {
                'room_name': chat['room_name'],
                'other_participant': other_participant[0] if other_participant else None,
                'last_message_preview': last_message_content,
                'chat_id': str(chat['_id'])
            }
            
            chat_previews.append(chat_preview)
        
        return Response(chat_previews, status=status.HTTP_200_OK)
