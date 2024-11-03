import datetime
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
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
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def create(self, request):
        participants = request.data.get('participants')
        if not participants or len(participants) < 2:
            return Response({"error": "At least two participants are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate a unique room name
        room_name = str(uuid.uuid4())
        
        # Create a new chat document
        chat_data = {
            'participants': participants,
            'room_name': room_name,
            'created_at': datetime.datetime.now()
        }
        
        result = db.chats.insert_one(chat_data)  # Insert into MongoDB
        
        return Response({
            "chat_id": str(result.inserted_id),
            "room_name": room_name,
            "participants": participants
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def send_message(self, request, room_name):
        message_data = {
            'room_name': room_name,
            'sender': request.data.get('sender'),
            'content': request.data.get('content'),
            'timestamp': request.data.get('timestamp', None)
        }
        
        result = db.messages.insert_one(message_data)
        
        message_data['_id'] = str(result.inserted_id)
        return Response(message_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def get_messages(self, request, room_name):
        messages = list(db.messages.find({'room_name': room_name}))
        
        for message in messages:
            message['_id'] = str(message['_id'])
        
        return Response(messages, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='user-chats')
    def get_user_chats(self, request):
        user_id = request.user.id 
        
        # Find all chats where the user is a participant
        chats = list(db.chats.find({'participants': user_id}))
        
        chat_previews = []
        for chat in chats:
            participants = chat['participants']
            
            other_participant = [p for p in participants if p != user_id]
            
            last_message = db.messages.find({'room_name': chat['room_name']}).sort('timestamp', -1).limit(1)
            last_message_content = next(last_message, {}).get('content', '')
            
            chat_preview = {
                'room_name': chat['room_name'],
                'other_participant': other_participant[0] if other_participant else None,
                'last_message_preview': last_message_content
            }
            
            chat_previews.append(chat_preview)
        
        return Response(chats, status=status.HTTP_200_OK)
