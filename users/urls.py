from django.urls import path
from .views import register_user, get_user, chat_with_assistant, get_user_threads

urlpatterns = [
    path('register/', register_user, name='register-user'),
    path('users/', get_user, name='users'),
    path('chat/', chat_with_assistant, name='chatbot'),
    path('api/threads/', get_user_threads, name='get_user_threads'),
]
