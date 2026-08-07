from contextlib import asynccontextmanager
from fastapi import FastAPI,Depends,Header,HTTPException,BackgroundTasks
from pydantic import BaseModel
from src.graph import build_graph
from src.vector_store import close_client
from src.ingest import main as ingest_main
from src.config import API_KEY
import logging
logging.basicConfig(level=logging.INFO,force=True)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    close_client()

app = FastAPI(lifespan=lifespan)
class QueryRequest(BaseModel):
    question:str
def verify_api_key(x_api_key:str = Header(...))->None:
    if x_api_key!=API_KEY:
        raise HTTPException(status_code=401,detail="Invalid API key")
@app.post("/query",dependencies=[Depends(verify_api_key)])
def query(request:QueryRequest)->dict:
    logger.info(f"Received question: {request.question}")
    state = build_graph()
    result = state.invoke({"question":request.question})
    logger.info(f"Received answer: {result['answer']}")
    return {"answer":result['answer'],"retrieved":result['retrieved']}
def run_ingest()->None:
    logger.info("Start of Ingestion")
    try:
        ingest_main([])
        logger.info("Finished Ingestion")
    except SystemExit:
        logger.warning("No PDFs found")
@app.post("/ingest",dependencies=[Depends(verify_api_key)])
def ingest(background_tasks:BackgroundTasks)->dict:
    background_tasks.add_task(run_ingest)
    logger.info("Ingestion queued")
    return {"status":"started"}
