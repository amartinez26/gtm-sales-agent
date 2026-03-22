import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

# --- THE CONTRACT ---
from config import PITCH_KEY 

# Load API Key
load_dotenv()

# --- SETUP ---
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = vector_db.as_retriever(search_kwargs={"k": 2})

# Using Gemini 3 Flash
llm = ChatGoogleGenerativeAI(model="gemini-3-flash", temperature=0.3)

system_prompt = (
    "You are a strategic GTM Sales Agent. Use the provided context to answer. "
    "Context: {context}"
)
prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{input}")])
combine_docs_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, combine_docs_chain)

# --- TEST SUITE ---
test_cases = [
    {"id": 1, "question": "Where did Stihl open their new battery plant in 2025?", "expected_mention": "Oradea, Romania"},
    {"id": 2, "question": "What is the specific sales goal for battery tools by 2027?", "expected_mention": "35%"},
    {"id": 3, "question": "What is Stihl's 'Dual Technology' strategy?", "expected_mention": "gasoline and battery"}
]

# --- EVALUATION LOOP ---
results = []
print(f"--- DEBUG: Using PITCH_KEY = '{PITCH_KEY}' ---")
print(f"--- Starting Evaluation of {len(test_cases)} cases ---\n")

for case in test_cases:
    print(f"Testing Case {case['id']}...")
    
    # 1. Invoke the chain
    response = rag_chain.invoke({"input": case["question"]})
    
    # 2. DEBUG PRINT: See everything LangChain returned
    # This will show us if the keys are 'answer', 'output', or something else
    print(f"   RAW KEYS RECEIVED: {list(response.keys())}")
    
    # 3. Extract the answer
    ai_text = response.get("answer", "")
    
    # 4. DEBUG PRINT: See the actual text found
    print(f"   AI TEXT FOUND: '{ai_text[:50]}...'") # Shows first 50 chars
    
    if not ai_text:
        print("   ⚠️ WARNING: AI returned an empty string!")

    is_passed = case["expected_mention"].lower() in ai_text.lower()
    
    results.append({
        "case_id": case["id"],
        "question": case["question"],
        "expected_keyword": case["expected_mention"],
        PITCH_KEY: ai_text, 
        "passed": is_passed,
        "timestamp": datetime.now().isoformat()
    })

# --- SAVE TO JSON ---
output_file = "eval_results.json"
with open(output_file, "w") as f:
    json.dump(results, f, indent=4)

print(f"\n--- Evaluation Complete! Check {output_file} for full details ---")