from pathlib import Path
from google import genai 
from google.genai import types 
from src.config import GEMINI_API_KEY,GEMINI_MODEL
_PROMPT = (
    "You are being given one or more document pages as images. "
    "Only answer from what is visible. "
    "Question: {question} "
    "If the pages don't contain the answer, say so."
)
def _image_part(image_path:Path)->types.Part:
    byte = Path(image_path).read_bytes()
    return types.Part.from_bytes(data=byte,mime_type="image/png")
def answer(question:str,pages:list[dict])->str:
    client = genai.Client(api_key=GEMINI_API_KEY)
    contents = []
    for page in pages:
        contents.append(f"--- {page['pdf']} - page {page['page_number']} ---")
        contents.append(_image_part(page['image_path']))
    contents.append(_PROMPT.format(question=question))
    return client.models.generate_content(model=GEMINI_MODEL,contents=contents).text
#answer the final question with the bytes of the image