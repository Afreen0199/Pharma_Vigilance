from pymilvus import (
    connections,
    utility,
    Collection
)

# ============================================
# CONNECT TO MILVUS
# ============================================

connections.connect(
    alias="default",
    host="localhost",
    port="19530"
)

print("\n✅ Connected to Milvus\n")

# ============================================
# LIST COLLECTIONS
# ============================================

collections = utility.list_collections()

print("📦 Collections:")
print(collections)

# ============================================
# FETCH ALL RECORDS FROM EACH COLLECTION
# ============================================

for collection_name in collections:

    print("\n" + "=" * 100)
    print(f"📂 COLLECTION: {collection_name}")
    print("=" * 100)

    collection = Collection(collection_name)

    # Load collection
    collection.load()

    total_entities = collection.num_entities

    print(f"\n🔹 Total Entities: {total_entities}")

    print("\n🔹 Schema:")
    print(collection.schema)

    print("\n🔹 Indexes:")
    print(collection.indexes)

    # ============================================
    # FETCH ALL RECORDS
    # ============================================

    print("\n🔹 Fetching ALL Records...\n")

    try:

        # Milvus query limit handling
        batch_size = 100
        offset = 0

        all_results = []

        while offset < total_entities:

            results = collection.query(
                expr='id != ""',
                limit=batch_size,
                offset=offset,
                output_fields=[
                    "id",
                    "text",
                    "analysis_id",
                    "drug_name",
                    "document_type",
                    "collection_type"
                ]
            )

            if not results:
                break

            all_results.extend(results)

            offset += batch_size

        # ============================================
        # PRINT ALL RECORDS
        # ============================================

        for idx, row in enumerate(all_results, start=1):

            print("\n" + "-" * 80)
            print(f"📄 RECORD {idx}")
            print("-" * 80)

            for key, value in row.items():

                # Trim extremely huge text for readability
                if isinstance(value, str) and len(value) > 1500:
                    value = value[:1500] + "\n...[TRUNCATED]..."

                print(f"\n{key}:")
                print(value)

        print(f"\n✅ Total Records Retrieved: {len(all_results)}")

    except Exception as e:

        print(f"\n❌ Error fetching records:")
        print(str(e))

print("\n✅ Full Milvus Inspection Complete\n")