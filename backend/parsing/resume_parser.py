from typing import List
import google.generativeai as genai
from dotenv import load_dotenv
import os 
import time
import pathlib

"""For now, chunking and embedding will only be implemented for the resume upload, 
for the MVP."""


def init_client():
    find_path = pathlib.Path(__file__).resolve()
    env_path = find_path.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv() # Fallback 
        
    api_key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not api_key:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not found in environment variables")
    
    genai.configure(api_key=api_key)

    


def genai_parse_pdf(
    pdf_path: str,
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
    You are a resume parser. Extract and structure the following information from this resume:
    
    1. Personal Information: Name, contact details
    2. Summary/Objective: Professional summary if present
    3. Work Experience: List all jobs with:
       - Company name
       - Job title
       - Duration
       - Key responsibilities and achievements
    4. Education: List all education with:
       - Institution name
       - Degree/qualification
       - Field of study
       - Graduation year
    5. Skills: List all technical and soft skills mentioned
    6. Projects: Any notable projects mentioned
    7. Certifications: Any certifications or licenses
    
    Return the information in a clear, structured JSON format.
    If a section is not present in the resume, return an empty list or null for that field.
    """
    
    model_instance = genai.GenerativeModel(model)
    model_response = model_instance.generate_content([uploaded_file, prompt])
    
    # Clean up: delete the file from Gemini servers
    genai.delete_file(uploaded_file.name)
    print(f"File deleted from Gemini servers")
    
    return {
        "raw_text": model_response.text,
        "file_name": uploaded_file.display_name,
    }
    
    
        