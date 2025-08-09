from .models import Conversation, Message 
from django.contrib import admin

# Register your models here.
class ConversationAdmin(admin.ModelAdmin):  # Inherit from ModelAdmin
    model = Conversation
    list_display = ('id', 'user', 'created_at', 'updated_at')


class MessageAdmin(admin.ModelAdmin):  # Inherit from ModelAdmin
    model = Message
    list_display = ('id', 'conversation', 'user_message', 'model_response', 'created_at')


# Register each model with its admin class separately
admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)