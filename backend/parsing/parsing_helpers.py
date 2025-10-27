from fastapi import UploadFile, File
import tempfile
import os
from resume_parser import genai_parse_pdf
from utils.embeddings import embed_resume_chunks


def parse_upload(file: UploadFile = File(...)):
     # Save to temporary file for processing
    file_bytes = file.file.read()  
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(file_bytes)
        tmp_path = tmp_file.name
    
        # Parse the PDF using Gemini
        print(f"Parsing resume: {file.filename}")
        parsed_resume = genai_parse_pdf(tmp_path, file.filename)
        
        print(f"Embedding chunks...")
        embedded_resume = embed_resume_chunks(parsed_resume)
        
        skills = []
        experience = []
        raw_text_parts = []
        
        # Extract skills and experience from chunks
        for chunk in embedded_resume['chunks']:
            section = chunk['section'].lower()
            content = chunk['content']
            
            raw_text_parts.append(f"{chunk['section']}:\n{content}\n")
            
            # Extract skills from skills section
            if 'skill' in section:
                skills.append(content)
            
            # Extract experience from work/experience sections
            if any(keyword in section for keyword in ['work', 'experience', 'employment']):
                experience.append(content)
            
            raw_text = "\n".join(raw_text_parts)
        
        return {
            "filename": file.filename,
            "raw_text": raw_text,
            "skills": skills,
            "experience": experience,
            "chunks": embedded_resume["chunks"]
        }
            
    os.remove(tmp_path)