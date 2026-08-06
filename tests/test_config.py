import pytest
from src.config import GEMINI_API_KEY,PDFS_DIR,PAGE_IMAGES_DIR,QDRANT_PATH,VECTOR_DIM
from pathlib import Path
def test_gemini_api_key_is_set():
    assert GEMINI_API_KEY # treats empty and none as falsy 
def test_directory_constants_are_paths():
    assert isinstance(PDFS_DIR,Path)
    assert isinstance(PAGE_IMAGES_DIR,Path)
    assert isinstance(QDRANT_PATH,Path)
def test_vector_dim_matches_model():
    assert VECTOR_DIM == 128 