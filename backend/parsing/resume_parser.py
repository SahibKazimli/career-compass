import google.generativeai as genai
from dotenv import load_dotenv
import os 
import time
import pathlib
import re
import json

"""For now, chunking and embedding will only be implemented for the resume upload, 
for the MVP."""


def init_client():
    find_path = pathlib.Path(__file__).resolve()
    env_path = find_path.parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv() # Fallback 
        
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)


    
def genai_parse_pdf(
    pdf_path: str,
    filename: str, 
    model: str = "gemini-2.5-flash"
):
    # Parse a PDF using Gemini's File API. 
    init_client()
    
    print(f"Uploading file: {pdf_path}")
    uploaded_file = genai.upload_file(pdf_path)
    
    print("Processing...")
    while uploaded_file.state.name == "PROCESSING":
        time.sleep(1)
        uploaded_file = genai.get_file(uploaded_file.name)
    
    if uploaded_file.state.name == "FAILED":
        raise ValueError(f"File processing failed: {uploaded_file.state}")
    
    print(f"File processed successfully: {uploaded_file.name}")
    
    # Create a structured prompt to extract resume information
    prompt = """
        Analyze this resume and break it down into logical sections.
        For each section you find, provide:
        1. section: The section name (e.g., "Work Experience", "Education", "Skills", "Summary", "Projects", "Certifications")
        2. content: The complete text content of that section (keep all details)
        3. summary: A brief 1-2 sentence summary of that section
        
        Return as a JSON array:
        [
          {
            "section": "Work Experience",
            "content": "Complete work experience text...",
            "summary": "Brief summary..."
          }
        ]
        
        Important:
        - Capture ALL sections in the resume
        - Keep full original text in "content" field
        - Create logical sections even if not clearly labeled in resume
        """
    
    model_instance = genai.GenerativeModel(model)
    model_response = model_instance.generate_content([uploaded_file, prompt])
    
    # Clean up: delete the file from Gemini servers
    genai.delete_file(uploaded_file.name)
    print(f"File deleted from Gemini servers")
    
    # Parse the JSON response
    text = model_response.text
    
    json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        text = json_match.group(1)
    
    try:
        chunks = json.loads(text)
        if not isinstance(chunks, list):
            raise ValueError("Expected JSON array")
    except (json.JSONDecodeError, ValueError):
            # Fallback if parsing fails
            print("Warning: Could not parse structured response, using fallback")
            chunks = [{
                "section": "Full Resume",
                "content": text,
                "summary": "Resume content"
            }]
            
    print(f"Successfully parsed {len(chunks)} sections")
        
    return {
            "filename": filename,
            "chunks": chunks,
            "total_chunks": len(chunks)
        }
