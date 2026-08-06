from fastapi import FastAPI
from pydantic import BaseModel
from src.graph import build_graph
from src.vector_store import close_client
from src.ingest import main as ingest_main
app = FastAPI()
class QueryRequest(BaseModel):
    question:str
@app.post("/query")
def query(request:QueryRequest)->dict:
    state = build_graph()
    try:
        result = state.invoke({"question":request.question})
    finally:
        close_client()
    return {"answer":result['answer'],"retrieved":result['retrieved']}
@app.post("/ingest")
def ingest()->dict:
    try:
        ingest_main([])
        return {"status":"done"}
    except SystemExit:
        return {"status":"error","message":"No PDFs found "}