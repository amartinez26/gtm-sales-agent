import os
from fastapi import FastAPI
from pydantic import BaseModel, create_model  # Added create_model
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel
from config import PITCH_KEY  # Our single source of truth
import uvicorn

# 1. Import your actual Agent from your agent.py file
from agent import agent_executor 

# 2. Load Environment & Initialize Vertex AI
load_dotenv()
vertexai.init(project=os.getenv("GOOGLE_CLOUD_PROJECT"), location="us-central1")

# 3. Setup FastAPI
app = FastAPI(title="GTM Sales Agent API")

# --- THE API CONTRACT ---

# Input Model: What the frontend MUST send
class PitchRequest(BaseModel):
    query: str

# Dynamic Output Model: This uses the PITCH_KEY variable as the field name.
# This ensures the backend PROMISES to send whatever key is in config.py.
PitchResponse = create_model("PitchResponse", **{PITCH_KEY: (str, ...)})

# -------------------------

@app.post("/pitch", response_model=PitchResponse)
async def get_pitch(request: PitchRequest):
    try:
        print(f"--- Incoming Query: {request.query} ---")
        
        # Call the LangChain RAG agent
        response = agent_executor.invoke({"input": request.query})
        
        # Extract the text
        pitch_text = response.get("output", "I'm sorry, I couldn't generate a strategy for that query.")
        
        print(f"--- AI Response Generated Successfully ---")
        
        # Use dictionary unpacking to return the correct key-value pair
        return PitchResponse(**{PITCH_KEY: pitch_text})
        
    except Exception as e:
        print(f"!!! BACKEND ERROR: {e} !!!")
        # Even in an error, we follow the contract
        return PitchResponse(**{PITCH_KEY: f"Backend Error: {str(e)}"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)