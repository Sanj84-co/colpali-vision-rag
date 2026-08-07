from fastapi import FastAPI,Depends,Header,HTTPException
from pydantic import BaseModel
from src.graph import build_graph
from src.vector_store import close_client
from src.ingest import main as ingest_main
from src.config import API_KEY
import logging 
logging.basicConfig(level=logging.INFO,force=True)
logger = logging.getLogger(__name__)
app = FastAPI()
class QueryRequest(BaseModel):
    question:str
def verify_api_key(x_api_key:str = Header(...))->None:
    if x_api_key!=API_KEY:
        raise HTTPException(status_code=401,detail="Invalid API key")
@app.post("/query",dependencies=[Depends(verify_api_key)])
def query(request:QueryRequest)->dict:
    logger.info(f"Received question: {request.question}")
    state = build_graph()
    try:
        result = state.invoke({"question":request.question})
    finally:
        close_client()
    logger.info(f"Received answer: {result['answer']}")
    return {"answer":result['answer'],"retrieved":result['retrieved']}
@app.post("/ingest",dependencies=[Depends(verify_api_key)])
def ingest()->dict:
    logger.info("Start of Ingestion")
    try:
        ingest_main([])
        logger.info("Finished Ingestion")
        return {"status":"done"}
    except SystemExit:
        logger.warning("No PDFs found")
        return {"status":"error","message":"No PDFs found "}
