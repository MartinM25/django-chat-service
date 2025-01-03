from django.urls import path
from .views import ChatViewSet

urlpatterns = [
    path('chats/', ChatViewSet.as_view({'post': 'create'}), name='create-chat'),
    path('chats/<str:chat_id>/send_message/', ChatViewSet.as_view({'post': 'send_message'}), name='send_message'),
    path('chats/<str:room_name>/get_messages/', ChatViewSet.as_view({'get': 'get_messages'}), name='get_messages'),
    path('chats/user-chats/', ChatViewSet.as_view({'get': 'get_user_chats'}), name='get-user-chats'), 
]
