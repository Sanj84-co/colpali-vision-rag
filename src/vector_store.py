#handles storing page multivectors in qdrant 
from qdrant_client import QdrantClient
from qdrant_client import models as qm
from src.config import QDRANT_PATH,COLLECTION_NAME,TOP_K,VECTOR_DIM
from pathlib import Path 
_client:QdrantClient|None = None 
def get_client()->QdrantClient:
    global _client#initializes client 
    if _client is None:#if none intializes o qdrant client
        _client = QdrantClient(path=str(QDRANT_PATH))
    return _client
def close_client()->None:
    global _client
    if _client is not None:
        _client.close()
        _client = None 
def ensure_collection(reset: bool = False)->None:
    #pages could get stale so you have to return or evict them
    client = get_client()
    if reset and client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)
    if not client.collection_exists(COLLECTION_NAME) :
        client.create_collection(collection_name=COLLECTION_NAME,vectors_config=qm.VectorParams(size=VECTOR_DIM,distance=qm.Distance.COSINE,multivector_config=qm.MultiVectorConfig(comparator=qm.MultiVectorComparator.MAX_SIM)))
def upsert_page(point_id:int, multivector:list[list[float]],pdf_name:str,page_number:int,image_path:Path)->None:
    client = get_client()
    client.upsert(collection_name=COLLECTION_NAME,points=[qm.PointStruct(id=point_id,vector=multivector,payload={"pdf":pdf_name,"page_number":page_number,"image_path":str(image_path)})])
#takes the processed pdf and add it to qdrant
def search(multivector:list[list[float]],top_k:int=TOP_K)-> list[dict]:
    client = get_client()
    response = client.query_points(collection_name=COLLECTION_NAME,query=multivector,limit=top_k,with_payload=True)
    return [{**point.payload,"score":round(point.score,4)} for point in response.points]
#maxsim is prdoem the cosine on each single vector path and returning the one with the highesh score. sum those scores at the end 
