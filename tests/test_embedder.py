import pytest
from PIL import Image
from src.embedder import embed_image

@pytest.mark.slow
def test_embed_image_produces_correct_shape():
    img = Image.new("RGB",(10,10),"white")
    results = embed_image(img)
    assert results != [] and all(len(result) == 128 for result in results)