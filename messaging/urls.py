from django.urls import path
from . import views

urlpatterns = [
    path('chat/<int:chat_id>/', views.ChatDetailView.as_view(), name='chat_detail'),
    path('messages/<int:chat_id>/', views.MessageListView.as_view(), name='message_list'),
]
