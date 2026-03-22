from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# 1. Load the existing database (don't create a new one, just read from folder)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# 2. Test query - asking about a specific detail from your text file
query = "What is Stihl's goal for battery powered tools in 2027?"
print(f"--- Searching for: '{query}' ---")

# 3. Search the DB for the top match
docs = vector_db.similarity_search(query, k=1)

# 4. Display the result
if docs:
    print("\n--- Match Found in Database! ---")
    print(f"Content: {docs[0].page_content}")
else:
    print("\n--- Error: No matches found. Check your ingest.py script. ---")