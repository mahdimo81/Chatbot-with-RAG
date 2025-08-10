from .models import Conversation 
from django.contrib import admin

# Register your models here.
class ConversationAdmin(admin.ModelAdmin):  # Inherit from ModelAdmin
    model = Conversation
    list_display = ('id', 'user', 'texts', 'created_at', 'updated_at')


# Register each model with its admin class separately
admin.site.register(Conversation, ConversationAdmin)