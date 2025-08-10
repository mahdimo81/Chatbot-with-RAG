from django.urls import path
from .views import ChatView

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat'),
    # path('conversations/', ConversationListView.as_view(), name='conversation-list'),
]