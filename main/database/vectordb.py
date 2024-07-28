from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer

embeding_model = "dunzhang/stella_en_1.5B_v5"

model = SentenceTransformer("infgrad/stella_en_1.5B_v5", trust_remote_code=True)
client = MilvusClient("milvus_demo.db")

def createUserVectorDb(username: str):
  client.create_collection(
    collection_name=f"conversation_{username}",
    dimension=1024
  )
  return client

def getUserCollection(username: str):
  client.get_load_state(collection_name=f"covnersation_{username}")
  return client


def checkDbexist(username: str) -> bool:
  client.has_collection(f"conversation_{username}")

def get_embedding(text):
  doc_embeddings = model.encode([text])
  return doc_embeddings


def insert_document(text, username, client):
  embedding = get_embedding(text)
  client.insert(
      collection_name=f'covnersation_{username}',
      data=[
          {'vector': embedding, 'text': [text]}
      ]
  )

def search_similar(query, client, username, top_k=3):
  query_embedding = get_embedding(query)
  search_params = {
      "metric_type": "L2",
      "params": {"nprobe": 10},
  }
  results = client.search(
      collection_name=f'covnersation_{username}',
      data=[query_embedding],
      limit=top_k,
      output_fields=['text'],
      search_params=search_params
  )
  return [hit['text'] for hit in results[0]]

if __name__ == "__main__":
  test_username = "test_user"
  created_client = createUserVectorDb(test_username)
  print(f"Created collection for {test_username}: {created_client is not None}")

  # Test getUserCollection
  user_collection = getUserCollection(test_username)
  print(f"Got user collection for {test_username}: {user_collection is not None}")

  # Test checkDbexist
  db_exists = checkDbexist(test_username)
  print(f"Database exists for {test_username}: {db_exists}")

  # Test get_embedding
  test_text = "This is a test sentence."
  embedding = get_embedding(test_text)
  print(f"Got embedding for test text: {embedding.shape}")

  # Test insert_document
  insert_document(test_text, test_username, user_collection)
  print(f"Inserted document: {test_text}")

  # Test search_similar
  query = "Another test sentence."
  similar_results = search_similar(query, test_username, user_collection)
  print(f"Similar results for '{query}':")
  for result in similar_results:
      print(f"- {result}")

  # Clean up (optional)
  client.drop_collection(f"conversation_{test_username}")
  client.drop_collection("documents")