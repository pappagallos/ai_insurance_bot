import os
import re
import json
from bs4 import BeautifulSoup

import fitz  # PyMuPDF
import pdfplumber
import pandas as pd
import html  # ← 이게 핵심입니다!

def extract_text_html(pdf_path):
    doc = fitz.open(pdf_path)
    html_pages = []

    for page_num, page in enumerate(doc, 1):
        raw_html = page.get_text("html")
        unescaped_html = html.unescape(raw_html)  # 이스케이프 문자 복원
        html_pages.append(f"<h2>Page {page_num} - 텍스트</h2>\n" + unescaped_html)

    return "\n".join(html_pages)

def extract_table_html(pdf_path):
    html_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            for table_idx, table in enumerate(tables, 1):
                df = pd.DataFrame(table[1:], columns=table[0])
                html_table = df.to_html(index=False, border=1)
                html_tables.append(f"<h3>Page {page_num} - 표 {table_idx}</h3>\n{html_table}")

    return "\n".join(html_tables)

def convert_pdf_to_combined_html(pdf_path):
    text_html = extract_text_html(pdf_path)
    table_html = extract_table_html(pdf_path)

    full_html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>PDF 변환 결과</title>
        <style>
            body {{ font-family: sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 30px; }}
            table, th, td {{ border: 1px solid #ccc; padding: 8px; }}
            h2, h3 {{ margin-top: 40px; }}
        </style>
    </head>
    <body>
        <h1>PDF 텍스트 및 표 변환 결과</h1>
        {text_html}
        <hr>
        {table_html}
    </body>
    </html>
    """

    return full_html


def html_to_dict_tree(element):
    # 텍스트 노드
    if isinstance(element, str):
        return {"type": "text", "text": html.unescape(element.strip())}

    if element.name is None:
        return None  # 주석이나 비정상적인 노드

    node = {
        "type": element.name,
    }

    # 텍스트 포함 시
    if element.string and element.string.strip():
        node["text"] = html.unescape(element.string.strip())

    # 자식 태그가 있는 경우
    children = []
    for child in element.children:
        child_node = html_to_dict_tree(child)
        if child_node:
            children.append(child_node)

    if children:
        node["children"] = children

    return node


def test_pdf2html_beautifulsoup(data_path, save_base_path):

    def get_grandparent_folder_name(file_path):
        # 파일의 직상위 폴더 경로 추출
        parent_folder = os.path.dirname(file_path)
        
        # 직상위 폴더의 상위 폴더명 추출
        grandparent_folder = os.path.dirname(parent_folder)
        
        # 직상위 폴더명 반환
        return os.path.basename(grandparent_folder)

    def html_parser(file_path, change_dict):
        # # HTML 파일 열기
        # with open(file_path, "r", encoding="utf-8-sig", errors="ignore") as file:
        #     html_content = file.read()
        html_content = convert_pdf_to_combined_html(file_path)
        
        # BeautifulSoup을 사용하여 HTML 파싱
        soup = BeautifulSoup(html_content, "html.parser")
        
        # 재귀적으로 HTML 요소를 계층적으로 탐색하는 함수
        def parse_element(element, change_dict):
            if not element or not hasattr(element, "name"):
                return None

            if change_dict and element.get_text(strip=True):
                text_data = element.get_text(strip=True)
                for key, value in change_dict.items():
                    text_data = text_data.replace(str(key), str(value))
            else:
                text_data = element.get_text(strip=True) if element.get_text(strip=True) else None

            parsed_data = {
                "file_path": os.path.basename(os.path.dirname(file_path)),
                "text": text_data,
                "children": []
            }

            for child in element.children:
                if isinstance(child, str):
                    continue
                child_data = parse_element(child, change_dict)
                if child_data:
                    parsed_data["children"].append(child_data)

            # 노드 전체가 비어 있으면 None 반환
            if not parsed_data["text"] and not parsed_data["children"]:
                return None

            return parsed_data


        # HTML의 body 요소부터 파싱 시작
        # parsed_html = parse_element(soup.body, change_dict)
        root_element = soup.body if soup.body is not None else soup
        parsed_html = parse_element(root_element, change_dict)


        return parsed_html

    def clean_tree(node):

        # node가 dict가 아니면 그대로 반환 (문자열이거나 다른 타입일 수 있음)
        if not isinstance(node, dict):
            return node

        # text 값이 "null" 또는 "index"인 경우 이 노드를 삭제 (None은 JSON에서 null로 매핑됨)
        if node.get("text") in (None, "null", "index") \
            or re.fullmatch(r"[!@#\$%\^&\*\(\)\+\-=_\[\]\{\}\|\\;:'\",.<>/?`~\s]+", node.get("text")) or re.fullmatch(r".+페이지 입니다\.", node.get("text")):
            return None

        # children이 있다면 재귀적으로 정리
        if "children" in node:
            cleaned_children = []
            for child in node["children"]:
                cleaned_child = clean_tree(child)
                if cleaned_child is not None:
                    cleaned_children.append(cleaned_child)
            node["children"] = cleaned_children

        return node

    def id_tagging_tree(cleaned_dict, file_path):
        """
        cleaned_dict에 대해 모든 노드에 고유한 infile_id, parent_infile_id를 부여하고
        최종적으로 원래 구조를 반환합니다.
        """
        def recursive_tag(node, file_name, current_id, parent_id):
            if node is None:
                return current_id  # 건너뛰기

            node["infile_id"] = f"{file_name}_{current_id}"
            node["parent_infile_id"] = f"{file_name}_{parent_id}" if parent_id is not None else None
            
            next_id = current_id + 1

            for child in node.get("children", []):
                if isinstance(child, dict):
                    next_id = recursive_tag(child, file_name, next_id, current_id)

            return next_id

        file_name = os.path.basename(os.path.dirname(file_path))

        if not isinstance(cleaned_dict, dict):
            raise TypeError("cleaned_dict는 dict 형식이어야 합니다.")
        recursive_tag(cleaned_dict, file_name, current_id=0, parent_id=None)
        return cleaned_dict

    def extract_nodes(tree):
        """
        트리 구조의 딕셔너리에서 모든 노드의 정보를 추출하여 리스트로 반환합니다.
        각 노드는 ['file_path', 'text', 'children', 'infile_id', 'parent_infile_id'] 정보를 포함합니다.
        """
        result = []

        def traverse(node):
            # 현재 노드에서 children을 따로 저장 후 제외
            children = node.get('children', [])
            node_info = {k: v for k, v in node.items() if k != 'children'}
            result.append(node_info)
            for child in children:
                traverse(child)

        traverse(tree)
        return result
    
    def find_all_files(path):
        file_paths = []

        if os.path.isfile(path):
            file_paths.append(path)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                if "_files" not in root:
                    for file in files:
                        full_path = os.path.join(root, file)
                        file_paths.append(full_path)

        return file_paths
    
    def get_filename_without_extension(file_path):
        base_name = os.path.basename(file_path)       # 경로 제거, 파일명만 남김
        name_without_ext = os.path.splitext(base_name)[0]  # 확장자 제거
        return name_without_ext

    # 중복 제거와 트리 구조 조정
    def remove_adjacent_duplicates_and_fix_tree(data):
        new_data = []
        text_seen = set()
        id_map = {}  # 기존 infile_id -> 새로운 infile_id 매핑

        for i, item in enumerate(data):
            text = item['text']
            infile_id = item['infile_id']
            parent_infile_id = item['parent_infile_id']

            # 중복 텍스트가 이전 항목과 같으면 제거
            if new_data and new_data[-1]['text'] == text:
                # 중복된 항목은 추가하지 않음, 매핑만 업데이트
                id_map[infile_id] = new_data[-1]['infile_id']
                continue

            # 부모 ID가 자기 자신이 아닌 경우만 처리
            if parent_infile_id in id_map:
                parent_infile_id = id_map[parent_infile_id]
            elif parent_infile_id == infile_id:
                # 자기 자신을 참조하는 잘못된 구조인 경우, 맨 앞 항목으로 연결
                parent_infile_id = new_data[0]['infile_id'] if new_data else None

            # 새로운 항목 생성
            new_item = {
                'file_path': item['file_path'],
                'text': text,
                'infile_id': infile_id,
                'parent_infile_id': parent_infile_id
            }

            new_data.append(new_item)
            id_map[infile_id] = infile_id  # 현재 infile_id도 매핑에 추가

        return new_data
        
    def html_table_to_dict(html_content):
        if html_content is None:
            # raise ValueError("html_content가 None입니다.")
            pass

        # 문자열인 경우 BeautifulSoup 객체로 파싱
        if isinstance(html_content, str):
            soup = BeautifulSoup(html_content, "html.parser")
        else:
            soup = html_content  # 이미 BeautifulSoup 객체일 경우

        tables = []

        for table in soup.find_all("table"):
            table_dict = {"type": "table", "children": []}
            
            for row in table.find_all("tr"):
                row_dict = {"type": "tr", "children": []}
                for cell in row.find_all(["td", "th"]):
                    cell_dict = {
                        "type": cell.name,
                        "text": cell.get_text(strip=True)
                    }
                    row_dict["children"].append(cell_dict)
                table_dict["children"].append(row_dict)
            
            tables.append(table_dict)

        return tables
    
    def html_folder_parser(folder_path, folder_name, change_dict):
        file_paths = find_all_files(folder_path)
        
        page_text_list = []        
        for file_path in file_paths:
            html_parsed = html_parser(file_path, change_dict)
            cleaned = clean_tree(html_parsed)
            tagged_dict = id_tagging_tree(cleaned, file_path)
            page_text_list_temp = extract_nodes(tagged_dict)
            page_text_list.extend(page_text_list_temp)

        # 처리된 결과
        result = remove_adjacent_duplicates_and_fix_tree(page_text_list)

        return result
    
    
    
    change_dict = {"\U0001F554": "애"}

    os.makedirs(save_base_path, exist_ok=True)


    for folder_name in os.listdir(data_path):
        folder_path = os.path.join(data_path, folder_name)

        # HTML 파싱 함수 호출
        page_text_list = html_folder_parser(folder_path, folder_name, change_dict)
        page_text_list_json = [json.dumps(page_text_dict, ensure_ascii=False) for page_text_dict in page_text_list]

        # 저장 경로 생성
        # save_path = os.path.join(save_base_path, folder_name)
        save_path = os.path.join(save_base_path)
        os.makedirs(save_path, exist_ok=True)
        

        # JSON 원형 저장
        with open(os.path.join(save_path, f"{os.path.splitext(folder_name)[0]}_pdf2html.dict.json"), "w", encoding="utf-8-sig") as f:
            json.dump(page_text_list, f, ensure_ascii=False, indent=4)

        # JSON 문자열 버전 저장
        with open(os.path.join(save_path, f"{os.path.splitext(folder_name)[0]}_pdf2html.json.json"), "w", encoding="utf-8-sig") as f:
            json.dump(page_text_list_json, f, ensure_ascii=False, indent=4)