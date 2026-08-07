from pathlib import Path
from google import genai 
from google.genai import types 
from tenacity import retry,stop_after_attempt,wait_exponential
from src.config import GEMINI_API_KEY,GEMINI_MODEL
from pydantic import BaseModel
import json 
class AnswerWithCitation(BaseModel):
    answer:str
    page_number:int
    bbox : list[float]
_PROMPT = (
    "You are being given one or more document pages as images. "
    "Only answer from what is visible. "
    "Question: {question} "
    "If the pages don't contain the answer, say so."
)
_RERANK_PROMPT = (
    "You are shown several candidate document pages, labeled Candidate 1, Candidate 2, etc. "
    "Question: {question} "
    "Which candidates actually contain information relevant to answering this question? "
    "Respond with ONLY the relevant candidate numbers, comma-separated, and nothing else. "
    "Example response format: 1, 3"
)
_CITATION_PROMPT = (
    "You are being given one or more document pages as images, each labeled with its PDF name and page number. "
    "Only answer from what is visible. "
    "Question: {question} "
    "Identify the specific page the answer came from, and the bounding box of the exact region "
    "on that page (e.g. one bar, one table cell, one line of text) that supports your answer. "
    "Give the bounding box as [left, top, right, bottom], each a number between 0 and 1, "
    "representing the fraction of the way across (left/right) and down (top/bottom) the page image. "
    "If the pages don't contain the answer, say so in the answer field."
)


def _image_part(image_path:Path)->types.Part:
    byte = Path(image_path).read_bytes()
    return types.Part.from_bytes(data=byte,mime_type="image/png")
@retry(stop=stop_after_attempt(3),wait=wait_exponential(multiplier=1,min=2,max=10))
def answer(question:str,pages:list[dict])->str:
    if not pages:
        return "No relevant pages were found to answer this question."
    client = genai.Client(api_key=GEMINI_API_KEY)
    contents = []
    for page in pages:
        contents.append(f"--- {page['pdf']} - page {page['page_number']} ---")
        contents.append(_image_part(page['image_path']))
    contents.append(_PROMPT.format(question=question))
    return client.models.generate_content(model=GEMINI_MODEL,contents=contents).text
#answer the final question with the bytes of the image
@retry(stop=stop_after_attempt(3),wait=wait_exponential(multiplier=1,min=2,max=10))

def rerank_pages(question:str,pages:list[dict])->list[dict]:
    client = genai.Client(api_key=GEMINI_API_KEY)
    contents = []
    for index,page in enumerate(pages):
        contents.append(f"--- Candidate {index+1} ---")
        contents.append(_image_part(page['image_path']))
    contents.append(_RERANK_PROMPT.format(question=question))
    text = client.models.generate_content(model=GEMINI_MODEL,contents=contents).text
    lis = []
    if text is None:
        return []
    for x in text.split(','):
        try:
            n= int(x.strip())
        except ValueError:
            continue
        lis.append(n)
    return [pages[n-1] for n in lis if n<=len(pages) and n>=1]
@retry(stop=stop_after_attempt(3),wait=wait_exponential(multiplier=1,min=2,max=10))

def answer_with_citation(question:str,pages:list[dict])-> AnswerWithCitation|None:
    if not pages:
        return None 
    client = genai.Client(api_key=GEMINI_API_KEY)
    contents = []
    for page in pages:
        contents.append(f"--- {page['pdf']} - page {page['page_number']} ---")
        contents.append(_image_part(page['image_path']))
    contents.append(_CITATION_PROMPT.format(question=question))
    text = client.models.generate_content(model=GEMINI_MODEL,contents=contents,config=types.GenerateContentConfig(response_mime_type="application/json",response_schema=AnswerWithCitation)).text
    try:
       ans = json.loads(text)
       return AnswerWithCitation(**ans)
    except ValueError:
        return None 

