import os 
from django.apps import AppConfig
from pymilvus import connections, Collection

class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'
    
    def ready(self):
        # Only run in main server mode (not in situations like migrate)
        if os.environ.get('RUN_MAIN') == 'true':
            self.connect_to_milvus()
    
    def connect_to_milvus(self):
        print("Connecting to Milvus...")
        
        # Connect to the already running Milvus instance
        connections.connect("default", host="127.0.0.1", port=19530)
        
        collection_name = "document_collection"
        self.collection = Collection(collection_name)
        self.collection.load()
        
        print("Connected to Milvus successfully.")