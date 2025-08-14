from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import ChatInputSerializer, ConversationSerializer
from .models import Conversation
from .services.thinker import ChatThinker


class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Step 1: Get and validate input data
            user = request.user
            serializer = ChatInputSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            conversation_id = serializer.validated_data.get("conversation_id")
            user_message = serializer.validated_data["message"]
            separator = "<<i!***MS***!i>>"

            # Step 2: Think about it and create response first (before any DB changes)
            thinker = ChatThinker()
            
            # If this is a new conversation, generate title first
            if not conversation_id:
                title = thinker.create_title(user_message)
                title_words = title.split(" ")[:10]
                short_title = " ".join(title_words)
            else:
                short_title = None  # Title won't change for existing conversations

            # Get existing texts if this is an existing conversation
            existing_texts = ""
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(id=conversation_id, user=user)
                    existing_texts = conversation.texts
                except Conversation.DoesNotExist:
                    return Response(
                        {"detail": "Conversation not found."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            
            # Generate response
            response_text = thinker.process_message(user.id, user_message, existing_texts)

            # Step 3: Now create/update conversation with all data
            if conversation_id:
                # Update existing conversation
                updated_texts = f"{existing_texts}{separator}{user_message}{separator}{response_text}"
                conversation.texts = updated_texts
                conversation.save()
            else:
                # Create new conversation only after successful response
                texts = f"{user_message}{separator}{response_text}"
                conversation = Conversation.objects.create(
                    user=user,
                    title=short_title,
                    texts=texts
                )
            
            # Step 4: Serialize and return response
            conversation_serializer = ConversationSerializer(conversation)
            return Response(
                {
                    "conversation": conversation_serializer.data,
                    "response": response_text,
                },
                status=status.HTTP_200_OK,
            )

        except:
            return Response(
                {
                    'detail': "An unexpected error occurred."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            conversations = Conversation.objects.filter(user=user)
            serializer = ConversationSerializer(conversations, many=True)
            
            # Remove texts field from each conversation
            conversations_data = serializer.data
            for conversation in conversations_data:
                if 'texts' in conversation:
                    del conversation['texts']
            
            return Response(
                {"conversations": conversations_data}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class GetMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, idx):
        user = request.user
        separator = "<<i!***MS***!i>>"
        try:
            try:
                conversation = Conversation.objects.get(user=user, id=idx)
            except Conversation.DoesNotExist:
                return Response(
                    {"error": "Conversation not found or access denied."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if not conversation.texts:
                return Response({"pairs": []}, status=status.HTTP_200_OK)

            texts_list = conversation.texts.split(separator)
            pairs = []

            for i in range(0, len(texts_list) - 1, 2):
                pairs.append([texts_list[i], texts_list[i + 1]])

            return Response({"pairs": pairs}, status=status.HTTP_200_OK)
        except:
            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class DeleteConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, idx):
        user = request.user
        try: 
            try:
                conv = Conversation.objects.get(user=user, id=idx)
                conv_id = conv.id
                conv.delete()
                return Response({
                    "detail": f"Conversation with id {conv_id} has been deleted."
                }, status=status.HTTP_200_OK)
            except Conversation.DoesNotExist:
                return Response(
                    {"detail": "Conversation not found or access denied."},
                    status=status.HTTP_404_NOT_FOUND,
                )        
        except:
            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
