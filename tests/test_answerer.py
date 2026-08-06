import pytest
from PIL import Image,ImageDraw
from src.answerer import answer
@pytest.mark.slow
def test_answer_reads_number_from_imaage(tmp_path):
    img = Image.new("RGB",(400,20),"white")
    d = ImageDraw.Draw(img,"RGB")
    d.text((50,2),"999",fill="black")
    out_path=tmp_path/"test.png"
    img.save(out_path)
    pages = [{"pdf":"test.pdf","page_number":5,"image_path":str(out_path)}]
    result = answer("What is the number?",pages)
    assert "999" in result 