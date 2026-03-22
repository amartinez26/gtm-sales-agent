import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Load API Key
load_dotenv()

# 1. Connect to our "Memory" (Updated to 2026 imports)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = vector_db.as_retriever(search_kwargs={"k": 2})

# 2. Initialize the "Voice" (Using Flash for higher quota and speed)
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview", 
    temperature=0.3
)

# 3. Define the "System Instructions"
system_prompt = (
    "You are a strategic Go-To-Market (GTM) Sales Agent. "
    "Use the following pieces of retrieved context to write a compelling, "
    "one-paragraph outreach message to a prospect.\n\n"
    "Context: {context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

# 4. Glue it all together
combine_docs_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, combine_docs_chain)

# 5. Run the Agent!
query = "Write a value prop for Stihl's VP of Ops regarding their 2027 battery goals."
print(f"--- Agent is thinking (using Flash)... ---")
response = rag_chain.invoke({"input": query})

print("\n--- FINAL GTM PITCH ---")
print(response["answer"])