import pandas as pd
from pymilvus import connections, utility, Collection

def export_milvus_to_csv(collection_name, output_file):
    # Connect to Milvus server
    connections.connect("default", host="127.0.0.1", port=19530)
    
    # Check if collection exists
    if not utility.has_collection(collection_name):
        print(f"Collection '{collection_name}' does not exist.")
        return
    
    # Get the collection
    collection = Collection(collection_name)
    collection.load()
    
    # Get the number of entities in the collection
    num_entities = collection.num_entities
    print(f"Found {num_entities} entities in collection '{collection_name}'")
    
    # Fields to export
    fields_to_export = ["id", "user_id", "content"]
    
    try:
        # Create empty DataFrame with our columns
        df = pd.DataFrame(columns=fields_to_export)
        
        # Try to get all data at once
        try:
            # Query all entities (using "id >= 0" as a simple filter that should match all)
            results = collection.query(
                expr="id >= 0",
                output_fields=fields_to_export,
                limit=num_entities  # Get all entities at once
            )
            
            # Convert results to DataFrame
            df = pd.DataFrame.from_records(results)[fields_to_export]
            print(f"Successfully retrieved {len(df)} entities in one query")
            
        except Exception as e:
            print(f"Full query failed, trying batch processing: {e}")
        
        # Write DataFrame to CSV
        df.to_csv(output_file, index=False)
        print(f"Successfully exported {len(df)} entities to {output_file}")
        
    except Exception as e:
        print(f"Error during export: {e}")
    finally:
        # Release collection from memory
        collection.release()
        connections.disconnect("default")

if __name__ == "__main__":
    # Configuration
    COLLECTION_NAME = "document_collection"
    OUTPUT_FILE = "milvus_data_export.csv"
    
    # Run the export
    export_milvus_to_csv(COLLECTION_NAME, OUTPUT_FILE)