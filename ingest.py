import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# 1. Load the data
print("--- Loading documents ---")
loader = DirectoryLoader('./data/stihl_intelligence', glob="./*.txt", loader_cls=TextLoader)
docs = loader.load()

# 2. Chunk the text (Break it into digestible pieces for the AI)
print("--- Splitting text into chunks ---")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(docs)

# 3. Create Embeddings (The mathematical "brain")
print("--- Generating vector embeddings (this may take a moment) ---")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 4. Store in ChromaDB
print("--- Saving to local database ---")
vector_db = Chroma.from_documents(
    documents=chunks, 
    embedding=embeddings, 
    persist_directory="./chroma_db"
)

print("--- Step I Complete: Vector Database Created! ---")