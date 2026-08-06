from pdf2image import convert_from_path
from PIL import Image
from pathlib import Path
from src.config import POPPLER_PATH,RENDER_DPI,PAGE_IMAGES_DIR
def pdf_to_images(pdf_path:Path,dpi:int=RENDER_DPI)-> list[Image.Image]:
    poppler=POPPLER_PATH if POPPLER_PATH else None#dont reused the import we dont wnr to shadow the conig. 
    return convert_from_path(str(pdf_path),dpi=dpi,fmt='RGB',poppler_path=poppler)#rgb is consistent green channel mode
def save_page_image(source_pdf:str,page_number:int,data:Image.Image)->Path:
    PAGE_IMAGES_DIR.mkdir(mode=511,parents=True,exist_ok=True)#find page_iamges or makes one
    stem = Path(source_pdf).stem
    output_path = PAGE_IMAGES_DIR / f"{stem}_page_{page_number}.png"#gets the output path
    data.save(output_path,format='PNG')#saves the data as a png 
    return output_path#return the output path for that page
