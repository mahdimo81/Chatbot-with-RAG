from django.urls import path
from .views import ChatView, ConversationListView, GetMessagesView, DeleteConversationView

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat'),
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('get-messages/<int:idx>', GetMessagesView.as_view(), name="get-messages"),
    path('del-conv/<int:idx>', DeleteConversationView.as_view(), name="del-conv")
]