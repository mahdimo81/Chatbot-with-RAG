from pymilvus import (
    connections,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection
)
from milvus import default_server
import time
import psutil

def kill_milvus_processes():
    """Kill all milvus.exe processes"""
    print("Search for existing Milvus processes...")
    killed = False
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'milvus.exe':
            print(f"Found running milvus.exe (PID: {proc.pid}), terminating...")
            proc.kill()
            killed = True
    if killed:
        time.sleep(3)  # Give time for process to terminate completely
    print("Search has been finished...")
    return killed

def init_milvus():
    # Kill any existing Milvus processes first
    kill_milvus_processes()

    print("Initializing Milvus...")

    # Set base directory
    default_server.set_base_dir('milvus_data')
    
    # Clean up previous instance
    connections.disconnect('default')
    default_server.stop()
    
    # Wait longer for complete shutdown
    time.sleep(5)
    
    # Start Milvus server with retry mechanism
    max_retries = 3
    for attempt in range(max_retries):
        try:
            default_server.start()
            break
        except Exception as e:
            print(f"Start attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                # One last attempt to kill processes before giving up
                kill_milvus_processes()
                raise RuntimeError("Failed to start Milvus after 3 attempts")
            time.sleep(5)
    
    # Connect to Milvus
    connections.connect("default", host="127.0.0.1", port=default_server.listen_port)
    
    # Collection setup
    dimension = 384
    collection_name = "document_collection"
 
    if utility.has_collection(collection_name):    
        collection = Collection(collection_name)
        collection.load()
        print(f"Collection '{collection_name}' loaded successfully.")
    else:
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="user_id", dtype=DataType.INT64),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension)
        ]
        schema = CollectionSchema(fields, description="Collection for document search")
        collection = Collection(name=collection_name, schema=schema)
        print(f"Collection '{collection_name}' created successfully.")
    
    index_params = {
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "params": {"nlist": 128}
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    print("Milvus initialized successfully.")
    
    return collection

if __name__ == "__main__":
    try:
        collection = init_milvus()
        
        while True:
            input_command = input("Write quit to shutdown the Milvus and exit: ")
            if str(input_command).lower() == "quit":
                print("\nShutting down Milvus...")
                connections.disconnect("default")
                default_server.stop()
                kill_milvus_processes()  # Ensure process is killed
                time.sleep(5)  # Longer wait for complete shutdown
                break
    except Exception as e:
        print(f"Fatal error: {e}")
        default_server.stop()
        kill_milvus_processes()
        exit(1)