from PIL import Image
from src import pdf_render
def test_save_page_images_creates_file(tmp_path,monkeypatch):
    monkeypatch.setattr(pdf_render,"PAGE_IMAGES_DIR",tmp_path)
    img = Image.new("RGB",(10,10),"white")
    path = pdf_render.save_page_image("test.pdf",1,img)
    assert path.exists()
