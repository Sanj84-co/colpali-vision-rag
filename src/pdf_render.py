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
def crop_citation(image_path:Path,bbox:list[float])->Path:
    img = Image.open(image_path)
    if(len(bbox)<4): raise ValueError("Too Short of length ")
    if not all(0<=v<=1 for v in bbox): raise ValueError("Not normalized")
    width = img.width
    height = img.height 
    coordinates = []
    for i in range(len(bbox)):
        if i%2==0:
            coordinates.append(bbox[i]*width)
        else:
            coordinates.append(bbox[i]*height)
    coordinates = [int(x) for x in coordinates]
    im = img.crop((coordinates[0],coordinates[1],coordinates[2],coordinates[3]))
    output_path = PAGE_IMAGES_DIR/f"{image_path.stem}_citation.png"
    im.save(output_path)
    return output_path