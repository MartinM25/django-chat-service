from django.urls import path
from . import views

urlpatterns = [
    path('chat/<int:chat_id>/', views.ChatDetailView.as_view(), name='chat_detail'),
    path('messages/<int:chat_id>/', views.MessageListView.as_view(), name='message_list'),
    path('chat/<str:room_name>/send_message/', views.ChatViewSet.as_view({'post': 'send_message'}), name='send_message'),
    path('chat/<str:room_name>/get_messages/', views.ChatViewSet.as_view({'get': 'get_messages'}), name='get_messages'),
]
