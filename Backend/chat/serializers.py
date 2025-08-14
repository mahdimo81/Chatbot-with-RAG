from rest_framework import serializers
from .models import Conversation

class ConversationSerializer(serializers.ModelSerializer):
    texts = serializers.CharField(write_only=True)  # Make texts write-only
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'texts', 'created_at', 'updated_at']
        
class ChatInputSerializer(serializers.Serializer):
    message = serializers.CharField()
    conversation_id = serializers.IntegerField(required=False)