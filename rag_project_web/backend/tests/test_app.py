from app import chunk_text, is_duplicate_document


def test_chunk_text_splits_with_overlap():
    text = "word " * 20

    chunks = chunk_text(text, chunk_size=10, overlap=3)

    assert len(chunks) > 1
    assert all(chunk for chunk in chunks)


def test_duplicate_document_detection():
    stored_chunks = [
        {"filename": "doc1.pdf"},
        {"filename": "doc2.pdf"},
    ]

    assert is_duplicate_document(stored_chunks, "doc1.pdf") is True
    assert is_duplicate_document(stored_chunks, "doc3.pdf") is False
