import os
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel

# 1. Load your credentials (Project ID: create-a-video-viewer)
load_dotenv()

# 2. Initialize the connection to Google Cloud
vertexai.init(project=os.getenv("GOOGLE_CLOUD_PROJECT"), location="us-central1")

# 3. Update to the 2026 Stable Model
# 'gemini-1.5-flash' is retired. 'gemini-2.5-flash' is the new standard.
model = GenerativeModel("gemini-2.5-flash")

def generate_gtm_pitch(company, news_context):
    """
    This function represents the 'Generation' layer.
    In the Search role, this is the 'Productizing' part of the JD.
    """
    prompt = f"""
    Role: Strategic Sales Engineer at Google Cloud.
    Input Data: {news_context}
    
    Task: Write a high-level, 2-sentence pitch to the CEO of {company}.
    Connect their recent news to a specific Google Cloud AI solution.
    Tone: Professional, visionary, and concise.
    """
    
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    # For now, we are 'hardcoding' the news. 
    # Next, we will build the Search engine to 'retrieve' this automatically.
    test_company = "Stihl"
    test_news = "Stihl is investing in global supply chain automation and AI-driven logistics for 2027."
    
    print(f"\n--- Testing GTM Agent: {test_company} ---\n")
    result = generate_gtm_pitch(test_company, test_news)
    print(result)