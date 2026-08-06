import torch
from colpali_engine.models import ColQwen2,ColQwen2Processor
from PIL import Image 
from src.config import COLPALI_MODEL
_model:ColQwen2|None = None
_processor:ColQwen2Processor|None = None 
def _device_and_dtype():
    if torch.cuda.is_available():
        return ("cuda",torch.bfloat16)
    else:
        return ("cpu",torch.float32)#get the specific device that and dtype we are running on
def load_model()->tuple[ColQwen2,ColQwen2Processor]:
    global _model, _processor
    if _model is not None and _processor is not None:
        return _model,_processor
    if _model is None:
        device,dtype = _device_and_dtype()
        _model = ColQwen2.from_pretrained(COLPALI_MODEL,torch_dtype = dtype, device_map = device).eval()
    if _processor is None:
        _processor = ColQwen2Processor.from_pretrained(COLPALI_MODEL)
    return _model,_processor

def _to_multivector(embedding:torch.Tensor)->list[list[float]]:#convert the tensor into a nested float
    return embedding.to(torch.float32).cpu().numpy().tolist()
#tensor an model weights need to run on teh same memory
#1 is the btach dimension
def embed_image(image:Image.Image)->list[list[float]]:
    model,processor = load_model()#load the model
    inputs = processor.process_images([image]).to(model.device)#switch to the same device
    with torch.no_grad():#no gradient caluclation because you are not training the model
        out = model(**inputs)
    return _to_multivector(out[0])#conver and reutn the multivector.
def embed_query(text:str)->list[list[float]]:
    model,processor = load_model()
    inputs = processor.process_queries([text]).to(model.device)
    with torch.no_grad():
        out = model(**inputs)
    return _to_multivector(out[0])