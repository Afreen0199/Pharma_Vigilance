import os
from pymilvus import MilvusClient

def inspect_milvus_db():
    milvus_uri = os.getenv("MILVUS_URI", "http://localhost:19530")
    print(f"Connecting to Milvus at {milvus_uri}...")
    
    try:
        client = MilvusClient(uri=milvus_uri)
        collections = client.list_collections()
        print(f"\nFound {len(collections)} collections: {collections}")
        
        for col_name in collections:
            print(f"\n{'='*60}")
            print(f"Collection: {col_name}")
            print(f"{'='*60}")
            
            # Describe collection schema
            desc = client.describe_collection(col_name)
            print(f"\nSchema Details:")
            for field in desc.get('fields', []):
                field_type = field.get('type') or field.get('dtype') or field.get('datatype', 'Unknown')
                print(f"  - {field['name']}: {field_type} (is_primary: {field.get('is_primary', False)})")
                
            # Get collection stats (row count)
            stats = client.get_collection_stats(col_name)
            print(f"\nStats: {stats}")
            
            # Query a few entries (empty filter matches everything, limit 3)
            # MilvusClient query requires a filter. We can use an ID condition that is always true, 
            # or just 'id != ""' assuming id is a string
            print("\nSample Data (First 3 entries):")
            try:
                # Querying with an always-true filter to get sample data
                res = client.query(collection_name=col_name, filter="id != ''", limit=5, output_fields=["*"])
                if res:
                    for i, item in enumerate(res):
                        print(f"\n--- Entry {i+1} ---")
                        for k, v in item.items():
                            if k == 'embedding':
                                print(f"  {k}: [Vector of size {len(v)}]")
                            elif isinstance(v, str) and len(v) > 100:
                                print(f"  {k}: {v[:100]}... [TRUNCATED]")
                            else:
                                print(f"  {k}: {v}")
                else:
                    print("  Collection is empty.")
            except Exception as e:
                print(f"  Error fetching sample data: {e}")
                
    except Exception as e:
        print(f"Failed to connect or query: {e}")

if __name__ == "__main__":
    inspect_milvus_db()
