"""
Create Faiss embedding file from Document

Created on 2025-05-22 by Seungwoon Shin
"""
from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

import time
import json
import os
import uuid
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from tqdm import tqdm

def process_table_data(table):
    """document 형식에 맞는 table 데이터 정제"""
    table_content = []
    
    # 헤더 추출
    if "headers" in table and table["headers"]:
        headers = table["headers"]
        table_content.append("표 헤더: " + " | ".join(headers))
    
    # 행 데이터 추출
    if "rows" in table:
        table_content.append("표 데이터:")
        for row in table["rows"]:
            # 빈 행 건너뛰기
            if any(cell.strip() for cell in row):
                row_text = " | ".join(row)
                table_content.append(row_text)
    
    # body_sections 처리 (개선된 테이블 구조)
    if "body_sections" in table:
        for section in table["body_sections"]:
            section_name = section.get("section_name", "섹션")
            table_content.append(f"{section_name}:")
            for row in section["rows"]:
                row_text = " | ".join([cell["text"] for cell in row])
                table_content.append(row_text)
    
    return "\n".join(table_content)

def convert_hierarchical_json_to_documents(json_data, file_name: str):
    """계층적 json파일을 document 형태로 변환"""
    documents = []
    
    for section_key, section_data in json_data.items():
        # 섹션 ID 생성
        section_id = str(uuid.uuid4())
        
        # 섹션 콘텐츠 추출
        section_content = ""
        if "content" in section_data:
            if isinstance(section_data["content"], list):
                section_content = "\n".join([str(item) for item in section_data["content"]])
            else:
                section_content = str(section_data["content"])
        
        # 섹션 메타데이터
        section_metadata = {
            "id": section_id,
            "parent_id": file_name,  # 최상위 노드
            "path": section_key,
            "depth": 0,
            "node_type": "section",
            "section_title": section_key
        }
        
        # 섹션 Document 생성
        section_doc = Document(
            page_content=f"섹션: {section_key}\n{section_content}",
            metadata=section_metadata
        )
        documents.append(section_doc)
        
        # 하위 섹션 처리
        if "subsections" in section_data and isinstance(section_data["subsections"], dict):
            for subsection_key, subsection_data in section_data["subsections"].items():
                # 하위 섹션 ID 생성
                subsection_id = str(uuid.uuid4())
                
                # 하위 섹션 콘텐츠 추출
                subsection_content = ""
                if "content" in subsection_data:
                    if isinstance(subsection_data["content"], list):
                        subsection_content = "\n".join([str(item) for item in subsection_data["content"]])
                    else:
                        subsection_content = str(subsection_data["content"])
                
                # 하위 섹션 메타데이터
                subsection_metadata = {
                    "id": subsection_id,
                    "parent_id": section_id,  # 부모 섹션 ID
                    "path": f"{section_key}/{subsection_key}",
                    "depth": 1,
                    "node_type": "subsection",
                    "section_title": section_key,
                    "subsection_title": subsection_key
                }
                
                # 하위 섹션 Document 생성
                subsection_doc = Document(
                    page_content=f"하위 섹션: {subsection_key}\n{subsection_content}",
                    metadata=subsection_metadata
                )
                documents.append(subsection_doc)
                
                # 테이블 처리
                if "tables" in subsection_data and isinstance(subsection_data["tables"], list):
                    for i, table in enumerate(subsection_data["tables"]):
                        table_content = process_table_data(table)
                        table_metadata = {
                            "id": str(uuid.uuid4()),
                            "parent_id": subsection_id,  # 부모 하위 섹션 ID
                            "path": f"{section_key}/{subsection_key}/table{i}",
                            "depth": 2,
                            "node_type": "table",
                            "section_title": section_key,
                            "subsection_title": subsection_key,
                            "table_index": i
                        }
                        table_doc = Document(
                            page_content=f"표 {i+1}:\n{table_content}",
                            metadata=table_metadata
                        )
                        documents.append(table_doc)
                
                # 하위 하위 섹션 처리
                if "subsections" in subsection_data and isinstance(subsection_data["subsections"], dict):
                    for subsubsection_key, subsubsection_data in subsection_data["subsections"].items():
                        # 재귀적으로 처리할 수도 있지만, 여기서는 3단계까지만 명시적으로 처리
                        subsubsection_id = str(uuid.uuid4())
                        
                        # 하위 하위 섹션 콘텐츠 추출
                        subsubsection_content = ""
                        if "content" in subsubsection_data:
                            if isinstance(subsubsection_data["content"], list):
                                subsubsection_content = "\n".join([str(item) for item in subsubsection_data["content"]])
                            else:
                                subsubsection_content = str(subsubsection_data["content"])
                        
                        # 하위 하위 섹션 메타데이터
                        subsubsection_metadata = {
                            "id": subsubsection_id,
                            "parent_id": subsection_id,  # 부모 하위 섹션 ID
                            "path": f"{section_key}/{subsection_key}/{subsubsection_key}",
                            "depth": 2,
                            "node_type": "subsubsection",
                            "section_title": section_key,
                            "subsection_title": subsection_key,
                            "subsubsection_title": subsubsection_key
                        }
                        
                        # 하위 하위 섹션 Document 생성
                        subsubsection_doc = Document(
                            page_content=f"하위 하위 섹션: {subsubsection_key}\n{subsubsection_content}",
                            metadata=subsubsection_metadata
                        )
                        documents.append(subsubsection_doc)
    
    return documents


def pretty_print_docs(docs):
    print(
        f"\n{'-' * 100}\n".join(
            [
                f"Document {i+1}:\n\n{d.page_content}\nMetadata: {d.metadata}"
                for i, d in enumerate(docs)
            ]
        )
    )

def get_document() -> Document:
    """ Transform from JSON to Document form"""
    all_documents = []
    h_jsons = [f for f in os.listdir('../../parser_upstage/hierarchical_data') if f.endswith('.json')]
    for idx, h_json in enumerate(h_jsons):
        with open(f'../../parser_upstage/hierarchical_data/{h_json}', "r", encoding="utf-8") as f:
            json_file = json.load(f)
            documents = convert_hierarchical_json_to_documents(json_file, h_json[:-5],)
            all_documents.extend(documents)
            print(f"총 {len(documents)}개의 {idx}번째 Document 객체가 생성되었습니다.")
    print(f"총 {len(all_documents)}개의 전체 Document 객체가 완성되었습니다.")

    return all_documents


def get_embedding():
    """
    벡터 임베딩 생성
    """
    if not os.path.exists("embed"):
        os.makedirs("embed")
    start_time = time.time()
    documents = get_document()
    # embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-exp-03-07",
    #                                           google_api_key=os.getenv("gemini.api.key"))
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    total_documents = len(documents)
    progress_bar = tqdm(total=total_documents, desc="Processing Documents")
    batch_size = 2
    for i in range(0, total_documents, batch_size):
        batch = documents[i:i+batch_size]
        
        if i == 0:
            vector_store = FAISS.from_documents(
                documents = batch,
                embedding=embeddings,
                docstore=InMemoryDocstore(),
                index_to_docstore_id={},
                distance_strategy = "COSINE"
            )

        else:
            vector_store.add_documents(batch)
        
        progress_bar.update(len(batch))

    vector_store.save_local(folder_path="embed")
    print("Faiss embedding completed.")
    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes, seconds = divmod(elapsed_time, 60)
    print(f"\n\n\033[1;95mTotal time:\033[0m {int(minutes)} min {round(seconds, 2)} sec.")

if __name__ == '__main__':
    get_embedding()
