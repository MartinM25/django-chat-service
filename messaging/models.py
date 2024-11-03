import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client["test-database"]

class Chat:
    def __init__(self, participants, creator):
        self.participants = participants
        self.creator = creator
        self.created_at = datetime.datetime.now()
        self.chat_id = None
        self.room_group_name = None

    def save(self):
        chat_data = {
            'participants': self.participants,
            'creator': self.creator,
            'created_at': self.created_at
        }
        result = db.chats.insert_one(chat_data)  # Insert into MongoDB
        self.chat_id = str(result.inserted_id)
        return self.chat_id

    @staticmethod
    def get_all_chats():
        return list(db.chats.find())

    @staticmethod
    def get_chat_by_id(chat_id):
        return db.chats.find_one({"_id": ObjectId(chat_id)})
    
    
class Message:
    def __init__(self, chat_id, sender, content):
        self.chat_id = chat_id
        self.sender = sender
        self.content = content
        self.timestamp = datetime.datetime.now()
        self.status = 'sent' 

    def save(self):
        message_data = {
            'chat_id': self.chat_id,
            'sender': self.sender,
            'content': self.content,
            'timestamp': self.timestamp,
            'status': self.status
        }
        message_id = db.messages.insert_one(message_data).inserted_id
        return message_id

    @staticmethod
    def get_messages_by_chat_id(chat_id):
        return list(db.messages.find({"chat_id": chat_id}))