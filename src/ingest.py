#turns the pdf into index
#ids needs to to be unique to page
import sys
from pathlib import Path
from src.config import PDFS_DIR
from src.embedder import embed_image
from src.pdf_render import pdf_to_images,save_page_image
from src.vector_store import close_client,ensure_collection,upsert_page

def ingest_pdf(pdf_path:Path,start_id:int)->int:
    images = pdf_to_images(pdf_path=pdf_path)
    for offset,image in enumerate(images):
        page_number = offset+1
        image_path = save_page_image(pdf_path.name,page_number,image)
        vector =embed_image(image)
        upsert_page(offset+start_id,vector,pdf_path.name,page_number,image_path)
    return start_id+len(images)#ingest into and return the star if plus mage 
def main(paths:list[str]):#if pdfs is truthy then it build path and adds if not checks for already uploaded path
    pdfs = [Path(p) for p in paths] if paths else sorted(PDFS_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs founde. Put a PDF in {PDFS_DIR} or pass a path")
        sys.exit()
    ensure_collection(reset=True)
    counter = 0
    for pdf in pdfs:
        counter = ingest_pdf(pdf,counter)
    print(f"Done. Indexed {counter} pages into Qdrant.")
if __name__=="__main__":
    try:
        main(sys.argv[1:])
    finally:
        close_client()