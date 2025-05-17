import os
import pymupdf4llm

from pdfminer.high_level import extract_text_to_fp


def test_pymupdf4llm(data_path, save_path):
    # 저장 경로가 존재하지 않으면 생성
    os.makedirs(save_path, exist_ok=True)

    for filename in os.listdir(data_path):
        if filename.lower().endswith('.pdf'):
            file_path = os.path.join(data_path, filename)
            llama_reader = pymupdf4llm.LlamaMarkdownReader()
            llama_docs = llama_reader.load_data(file_path)

            full_text = "".join(doc.text for doc in llama_docs)
            full_text = full_text.replace("\n\n", "\n").replace("\n\n\n", "")

            save_file_path = os.path.join(save_path, f"{os.path.splitext(filename)[0]}_pymupdf4llm.txt")
            with open(save_file_path, 'w', encoding='utf-8') as fp:
                fp.write(full_text)