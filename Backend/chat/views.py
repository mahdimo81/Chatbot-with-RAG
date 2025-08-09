from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import ChatInputSerializer, ConversationSerializer, MessageSerializer
from .models import Conversation, Message
from .services.thinker import ChatThinker

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Step 1: Get data from user
        user = request.user
        serializer = ChatInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        conversation_id = serializer.validated_data.get('conversation_id')

        user_message = serializer.validated_data['message']
        
        # Step 2: Think about it and create response
        thinker = ChatThinker()
        response_text = thinker.process_message(user.id, user_message)

        # Step 3: Manage conversation
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id, user=user)
            except Conversation.DoesNotExist:
                return Response({"detail": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            conversation = Conversation.objects.create(user=user)

        # Step 4: Save message and its reply
        Message.objects.create(
            conversation=conversation,
            user_message=user_message,
            model_response=response_text,
        )

        # Step 5: Serialize and return response
        conversation_serializer = ConversationSerializer(conversation)
        return Response({
            "conversation": conversation_serializer.data,
            "response": response_text,
        }, status=status.HTTP_200_OK)