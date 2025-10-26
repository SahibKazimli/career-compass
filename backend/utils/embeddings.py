import google.generativeai as genai
import numpy as np
from dotenv import load_dotenv
import pathlib
from typing import List, Dict

"""For now, I'll implement chunking and embedding for the resume uploads, as
well as the user inputs to the LLM. The webscraping will be implemented later, after
I've created the MVP."""

def init_client():
    find_path = pathlib.Path(__file__).resolve()
    env_path = find_path.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv() # Fallback 


def embed_resume_chunks(
    parsed_resume: Dict[str],
    model: str = "models/text-embedding-004",
) -> Dict[str]:
    """
    Embed all chunks from a parsed resume.
    
    Args:
        parsed_resume: Output from resume_parser.genai_parse_pdf()
        model: The embedding model to use
        
    Returns:
        Dictionary with embedded chunks and metadata
    """
    
    init_client()
    
    chunks = parsed_resume[chunks]
    
    texts_to_embed = [
        f"{chunk['section']}: {chunk['content']}"
        for chunk in chunks
    ]
    
    print(f"Embedding {len(chunks)} chunks...")
    
    try:
        # Generate embeddings in batch
        result = genai.embed_content(
            model=model,
            content=texts_to_embed,
        )
        embeddings = result['embedding']
        
        # Combine embeddings with original chunks
        embedded_chunks = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            embedded_chunks.append({
                "section": chunk['section'],
                "content": chunk['content'],
                "summary": chunk['summary'],
                "embedding": embedding,
                "embedding_dim": len(embedding)
            })
            print("Embedded all section chunks")
        
        return {
            "filename": parsed_resume['filename'],
            "chunks": embedded_chunks, 
            "total_chunks": len(embedded_chunks),
            "model": model
        }    
        
    except Exception as e:
        print(f"Embedding failed: {e}")


def compute_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    cosine = dot_product/ (norm1*norm2)
    return cosine
    
    
    