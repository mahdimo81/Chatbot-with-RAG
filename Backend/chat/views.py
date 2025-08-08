from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import ChatInputSerializer, ConversationSerializer, MessageSerializer
from .models import Conversation, Message
from .services.thinker import ChatThinker
from django.apps import apps
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = ChatInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_message = serializer.validated_data['message']
        conversation_id = serializer.validated_data.get('conversation_id')

        thinker = ChatThinker()

        # Step 1: Analyze the message
        extracted_data, retrieval_terms = thinker.analyze_message(user_message)

        old_informations = ""
        informations_to_save = None
        if extracted_data:
            for text in map(str.strip, extracted_data.split("|")):
                if not text:
                    continue

                search_embedding = model.encode([text])[0].tolist()
                search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

                results = apps.get_app_config('chat').collection.search(
                    data=[search_embedding],
                    anns_field="embedding",
                    param=search_params,
                    limit=5,
                    output_fields=["user_id", "content"],
                    expr=f"user_id == {user.id}"
                )

                if results:
                    for res in results:
                        content = res.get('content', '')
                        if content:
                            old_informations += content + " | "

            old_informations = old_informations.rstrip(" | ")
            informations_to_save = thinker.compare(old_informations, extracted_data)

        if informations_to_save:
            texts = [text.strip() for text in informations_to_save.split("|") if text.strip()]
            documents = []
            for text in texts:
                documents.append({'user_id': user.id, 'content': text})

            embeddings = model.encode([doc["content"] for doc in documents])
            data = [
                [doc["user_id"] for doc in documents],
                [doc["content"] for doc in documents],
                embeddings.tolist()
            ]
            insert_result = apps.get_app_config('chat').collection.insert(data)

        # Step 2: Handle retrieval terms
        informations = ""
        if retrieval_terms:
            for text in map(str.strip, retrieval_terms.split("|")):
                if not text:
                    continue

                search_embedding = model.encode([text])[0].tolist()
                search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

                results = apps.get_app_config('chat').collection.search(
                    data=[search_embedding],
                    anns_field="embedding",
                    param=search_params,
                    limit=5,
                    output_fields=["user_id", "content"],
                    expr=f"user_id == {user.id}"
                )

                if results:
                    for res in results:
                        content = res.get('content', '')
                        if content:
                            informations += content + " | "

            informations = informations.rstrip(" | ")

        # Step 3: Manage conversation
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id, user=user)
            except Conversation.DoesNotExist:
                return Response({"detail": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            conversation = Conversation.objects.create(user=user)

        # Step 4: Generate response
        response_text = thinker.generate_response(user_message, retrieved_data=informations if informations else None)

        # Step 5: Save messages separately
        # User's message
        Message.objects.create(
            conversation=conversation,
            user_message=user_message,
            model_response=response_text,
        )

        # Step 6: Serialize and return response
        conversation_serializer = ConversationSerializer(conversation)
        return Response({
            "conversation": conversation_serializer.data,
            "response": response_text,
        }, status=status.HTTP_200_OK)