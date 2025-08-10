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
        # Step 1: Get data from user
        user = request.user
        serializer = ChatInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        conversation_id = serializer.validated_data.get("conversation_id")
        user_message = serializer.validated_data["message"]
        separator = "<<i!***MS***!i>>"

        # Step 2: Think about it and create response
        thinker = ChatThinker()
        response_text = thinker.process_message(user.id, user_message)

        # Step 3: Manage conversation
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id, user=user)
                updated_texts = f"{conversation.texts}{separator}{user_message}{separator}{response_text}"
                conversation.texts = updated_texts
                conversation.save()
            except Conversation.DoesNotExist:
                return Response(
                    {"detail": "Conversation not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            texts = f"{user_message}{separator}{response_text}"
            conversation = Conversation.objects.create(user=user, texts=texts)

        # Step 4: Serialize and return response
        conversation_serializer = ConversationSerializer(conversation)
        return Response(
            {
                "conversation": conversation_serializer.data,
                "response": response_text,
            },
            status=status.HTTP_200_OK,
        )


class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            conversations = Conversation.objects.filter(user=user)
            serializer = ConversationSerializer(conversations, many=True)

            return Response(
                {"conversations": serializer.data}, status=status.HTTP_200_OK
            )
        except:
            return Response(
                {"detail": "There is a problem in server."},
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
                    {"error": "Conversation not found or access denied"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if not conversation.texts:
                return Response({"pairs": []}, status=status.HTTP_200_OK)

            texts_list = conversation.texts.split(separator)
            pairs = []

            for i in range(0, len(texts_list) - 1, 2):  # Fixed: removed keyword arguments
                pairs.append([texts_list[i], texts_list[i + 1]])

            return Response({"pairs": pairs}, status=status.HTTP_200_OK)
        except:
            return Response(
                {"detail": "There is a problem in server."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )