import os
from milvus import default_server
from django.apps import AppConfig
from pymilvus import connections, utility, Collection, DataType, FieldSchema, CollectionSchema

class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'
    
    def ready(self):
        # Only run in main server mode (not in situations like migrate)
        if os.environ.get('RUN_MAIN') == 'true':
            self.init_milvus()
    
    def init_milvus(self):
        print("Initializing Milvus...")

        # Specify where the data will be stored.
        default_server.set_base_dir('milvus_data')
        
        connections.disconnect('default')
        default_server.stop()
        
        default_server.start()
        connections.connect("default", host="127.0.0.1", port=default_server.listen_port)
        
        dimension = 384
        collection_name = "document_collection"
     
        if utility.has_collection(collection_name):    
            self.collection = Collection(collection_name)
            self.collection.load()
            print(f"Collection '{collection_name}' loaded successfully.")
        else:
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="user_id", dtype=DataType.INT64),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=500),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension)
            ]
            schema = CollectionSchema(fields, description="Collection for document search")
            self.collection = Collection(name=collection_name, schema=schema)
            print(f"Collection '{collection_name}' created successfully.")
        
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128}
        }
        self.collection.create_index(field_name="embedding", index_params=index_params)
        print("Milvus initialized successfully.")
