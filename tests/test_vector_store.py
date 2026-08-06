from src import vector_store
def test_upsert_and_search_roundtrip(tmp_path,monkeypatch):
    monkeypatch.setattr(vector_store,"QDRANT_PATH",tmp_path)
    monkeypatch.setattr(vector_store,"_client",None)
    vector_store.ensure_collection(reset=True)
    vector_store.upsert_page(0,[[1.0]*128],"doc_a.pdf",1,"fake_a.png")
    vector_store.upsert_page(1,[[0.0]*128],"doc_b.pdf",1,"fake_b.png")
    pdf = vector_store.search([[1.0]*128])[0]["pdf"]
    assert pdf =="doc_a.pdf"
    vector_store.close_client()