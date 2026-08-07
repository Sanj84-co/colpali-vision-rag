from dotenv import load_dotenv
import os
from pathlib import Path
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')# the ,model itself
POPPLER_PATH = None #tells pdf2image where to find the poppler program 
ROOT_DIR = Path(__file__).resolve().parent.parent#absolute path to your project's root folder
PDFS_DIR = ROOT_DIR/ 'pdfs' #goes to the pdf fp;der
PAGE_IMAGES_DIR = ROOT_DIR / 'page_images'
QDRANT_PATH = ROOT_DIR / 'qdrant_data'
COLPALI_MODEL = "vidore/colqwen2-v1.0"#it is model that handles the indetifying which images
RENDER_DPI = 150
COLLECTION_NAME = 'pdf_pages'
VECTOR_DIM = 128#fixed property of colqwen on how many dimensional vectors it can produce
TOP_K = 3
GEMINI_MODEL = 'gemini-3.5-flash'
RERANK_CANDIDATES = 10
API_KEY = os.getenv('API_KEY')