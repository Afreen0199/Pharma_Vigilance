from pymilvus import (
    connections,
    utility,
    Collection
)

# ==============================
# CONNECT TO MILVUS
# ==============================

connections.connect(
    alias="default",
    host="localhost",
    port="19530"
)

print("\n✅ Connected to Milvus\n")

# ==============================
# LIST ALL COLLECTIONS
# ==============================

collections = utility.list_collections()

print("📦 Collections Found:")
print(collections)

# ==============================
# LOOP THROUGH COLLECTIONS
# ==============================

for collection_name in collections:

    print("\n" + "=" * 60)
    print(f"📂 COLLECTION: {collection_name}")
    print("=" * 60)

    try:
        collection = Collection(collection_name)

        # Load collection
        collection.load()

        # Basic Info
        print(f"\n🔹 Number of Entities: {collection.num_entities}")

        print("\n🔹 Schema:")
        print(collection.schema)

        print("\n🔹 Indexes:")
        print(collection.indexes)

        # ==============================
        # FETCH SAMPLE DATA
        # ==============================

        print("\n🔹 Sample Records:")

        results = collection.query(
            expr='id != ""',
            limit=5,
            output_fields=[
                "id",
                "text",
                "analysis_id",
                "drug_name",
                "document_type",
                "collection_type"
            ]
        )

        if results:
            for idx, row in enumerate(results, 1):

                print(f"\n----- Record {idx} -----")

                for key, value in row.items():

                    # Trim huge text
                    if isinstance(value, str) and len(value) > 300:
                        value = value[:300] + "..."

                    print(f"{key}: {value}")

        else:
            print("⚠️ No data found.")

        # ==============================
        # ADD VECTOR SEARCH TEST
        # ==============================
        print("\n🔹 Running Semantic Vector Search Test...")
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer("all-MiniLM-L6-v2")
            query_embedding = model.encode("warfarin bleeding").tolist()

            search_results = collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param={
                    "metric_type": "L2",
                    "params": {"nprobe": 10}
                },
                limit=3,
                output_fields=[
                    "text",
                    "drug_name",
                    "document_type"
                ]
            )

            if search_results:
                for hits in search_results:
                    for s_idx, hit in enumerate(hits, 1):
                        print(f"\n--- Search Hit {s_idx} (Distance: {hit.distance:.4f}) ---")
                        txt = hit.entity.get('text')
                        if txt and len(txt) > 300:
                            txt = txt[:300] + "..."
                        print(f"text: {txt}")
                        print(f"drug_name: {hit.entity.get('drug_name')}")
                        print(f"document_type: {hit.entity.get('document_type')}")
            else:
                print("⚠️ No search results found.")
        except Exception as search_err:
            print(f"❌ Error during vector search: {search_err}")

    except Exception as e:
        print(f"\n❌ Error in collection '{collection_name}'")
        print(str(e))

print("\n✅ Inspection Complete\n")