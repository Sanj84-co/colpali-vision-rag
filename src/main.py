#builds the grqph ivokes with question and prints the retrieved paes
import sys
from src.graph import build_graph
from src.vector_store import close_client
def run(question:str)->None:
    graph = build_graph()
    try:
        result = graph.invoke({"question":question})
    finally:
        close_client()
    for retrieve in result["retrieved"]:
        print(f" {retrieve["pdf"]} - page{retrieve["page_number"]} - score{retrieve["score"]}")
    print(result["answer"])

if __name__=="__main__":
    if len(sys.argv)<2:
        print("No argument")
        sys.exit(1)
    else:
        run(" ".join(sys.argv[1:]))
