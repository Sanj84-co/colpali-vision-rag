#wires embed query into two step pipleine
from typing import TypedDict
from langgraph.graph import END,START,StateGraph
from src.answerer import rerank_pages,answer as gemini_answer
from src.embedder import embed_query
from src.vector_store import search
from src.config import RERANK_CANDIDATES
class RagState(TypedDict):
    question:str
    retrieved: list[dict]
    answer:str
def retrieve_node(state:RagState)->dict:#retrieveal portion of the pipeline take cyurrent state and pulls out the vector
    vector = embed_query(state["question"])
    retrieved = search(vector,top_k=RERANK_CANDIDATES)
    return {"retrieved":retrieved}
def rerank_node(state:RagState)->dict:
    retrieved = rerank_pages(state["question"],state["retrieved"])
    return {"retrieved":retrieved}
def answer_node(state:RagState)->dict:#the generation reds questyion and retrieved and retyurns n Bwer
    answer = gemini_answer(state["question"],state["retrieved"])
    return {"answer":answer}
def build_graph():#builds the graph to return the final answer
    builder = StateGraph(RagState)
    builder.add_node("retrieve",retrieve_node)
    builder.add_node("answer",answer_node)
    builder.add_node("rerank",rerank_node)
    builder.add_edge(START,"retrieve")
    builder.add_edge("retrieve","rerank")
    builder.add_edge("rerank","answer")
    builder.add_edge("answer",END)
    return builder.compile()