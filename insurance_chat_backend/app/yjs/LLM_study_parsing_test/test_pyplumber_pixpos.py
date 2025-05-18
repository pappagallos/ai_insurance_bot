import os
import re
import json
import pdfplumber
from collections import defaultdict

# --- 좌/우 분할 및 표 처리 도우미 ---
def split_by_half_x(items, page_width, key):
    half = page_width / 2
    left = [item for item in items if key(item) < half]
    right = [item for item in items if key(item) >= half]
    return left, right

def group_words_by_line(words, y_tolerance=3):
    lines = defaultdict(list)
    for word in words:
        assigned = False
        for key in lines:
            if abs(word['top'] - key) <= y_tolerance:
                lines[key].append(word)
                assigned = True
                break
        if not assigned:
            lines[word['top']].append(word)
    return list(lines.values())

def is_in_table(word, table_bboxes):
    for x0, top, x1, bottom in table_bboxes:
        if x0 <= word['x0'] <= x1 and top <= word['top'] <= bottom:
            return True
    return False

def get_table_bboxes(tables):
    return [table.bbox for table in tables]

# --- 페이지 단위 추출 ---
def process_region(region_words, region_tables):
    elements = []
    lines = group_words_by_line(region_words)
    for line in lines:
        line_text = " ".join(
            word['text'] for word in sorted(line, key=lambda w: w['x0'])
            if not is_in_table(word, [t.bbox for t in region_tables])
        )
        if line_text.strip():
            avg_top = sum(word['top'] for word in line) / len(line)
            elements.append({"type": "text", "top": avg_top, "content": line_text.strip()})

    for table in region_tables:
        cleaned_table = [
            [cell.strip() if cell else "" for cell in row]
            for row in table.extract()
        ]
        elements.append({"type": "table", "top": table.bbox[1], "content": cleaned_table})

    elements.sort(key=lambda e: e['top'])
    return elements

def extract_page_elements(page):
    page_width = page.width
    words = page.extract_words()
    tables = page.find_tables()
    word_left, word_right = split_by_half_x(words, page_width, lambda w: w['x0'])
    table_left, table_right = split_by_half_x(tables, page_width, lambda t: t.bbox[0])
    return [process_region(word_left, table_left), process_region(word_right, table_right)]

# --- 표를 Markdown으로 변환 ---
def table_json_to_markdown(table_json):
    if not table_json or not any(table_json):
        return ""
    cleaned_table = [[re.sub(r"\s*\n\s*", " ", cell.strip()) if cell else "" for cell in row] for row in table_json]
    header = "| " + " | ".join(cleaned_table[0]) + " |"
    separator = "| " + " | ".join(["---"] * len(cleaned_table[0])) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in cleaned_table[1:]]
    return "\n".join([header, separator] + rows)

# --- 전체 PDF 처리 ---
def extract_text_and_tables_to_txt(pdf_path, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.basename(pdf_path)
    output_file_path = os.path.join(save_dir, f"{os.path.splitext(filename)[0]}_pyplumber_pixpos.json.txt")
    full_text = ""

    with open(output_file_path, "w", encoding="utf-8-sig") as f_out:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                elements = extract_page_elements(page)
                for region_elements in elements:
                    for el in region_elements:
                        if el["type"] == "text":
                            f_out.write(el["content"] + "\n")
                            full_text += el["content"] + "\n"
                        elif el["type"] == "table":
                            table_json = json.dumps({"table": el["content"]}, ensure_ascii=False)
                            f_out.write(table_json + "\n")
                            full_text += table_json + "\n"
                f_out.write("\n\n")
                full_text += "\n\n"

    # print(f"✅ json 파일 저장 완료: {output_file_path}")
    return full_text

# --- 텍스트 + 테이블 markdown 변환 ---
def text_and_tables(document: str):
    chunks = []
    buffer = ""
    for line in document.splitlines():
        line = line.strip()
        if line.startswith("{\"table\":"):
            if buffer.strip():
                chunks.append(buffer.strip())
                buffer = ""
            try:
                table_data = json.loads(line)
                table_md = table_json_to_markdown(table_data["table"])
                chunks.append(table_md)
            except json.JSONDecodeError:
                print("⚠️ 잘못된 테이블 JSON:", line)
        else:
            buffer += line + " "
    if buffer.strip():
        chunks.append(buffer.strip())
    return chunks

# --- 전체 실행 함수 ---
def test_pyplumber_pixpos(data_path, save_path):
    os.makedirs(save_path, exist_ok=True)
    for filename in os.listdir(data_path):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(data_path, filename)
            raw_text = extract_text_and_tables_to_txt(pdf_path, save_path)
            combined = text_and_tables(raw_text)
            output_file_path = os.path.join(save_path, f"{os.path.splitext(filename)[0]}_pyplumber_pixpos.markdown.txt")
            with open(output_file_path, "w", encoding="utf-8") as fp:
                fp.write("\n\n".join(combined))
            # print(f"✅ Markdown 저장 완료: {output_file_path}")
            

# import os
# import re
# import json
# import pdfplumber

# # # --- Step 1: 표 영역 추출 ---
# def split_by_half_x(items, page_width, key):
#     """x 좌표 기준으로 왼쪽/오른쪽 나누기 (key는 함수)"""
#     half = page_width / 2
#     left = [item for item in items if key(item) < half]
#     right = [item for item in items if key(item) >= half]
#     return left, right


# def group_words_by_line(words, y_tolerance=3):
#     """단어들을 y좌표(top) 기준으로 한 줄로 묶기"""
#     from collections import defaultdict
#     lines = defaultdict(list)
#     for word in words:
#         assigned = False
#         for key in lines:
#             if abs(word['top'] - key) <= y_tolerance:
#                 lines[key].append(word)
#                 assigned = True
#                 break
#         if not assigned:
#             lines[word['top']].append(word)
#     return list(lines.values())

# def is_in_table(word, table_bboxes):
#     """단어가 표 안에 포함되어 있는지 판단"""
#     for x0, top, x1, bottom in table_bboxes:
#         if x0 <= word['x0'] <= x1 and top <= word['top'] <= bottom:
#             return True
#     return False

# def get_table_bboxes(tables):
#     """표들의 bbox를 리스트로 추출"""
#     return [table.bbox for table in tables]


# # --- Step 3: 텍스트와 표를 y좌표 기준으로 병합하여 하나의 텍스트로 만들기 ---
# def process_region(region_words, region_tables):
#     elements = []

#     lines = group_words_by_line(region_words)
#     for line in lines:
#         line_text = " ".join(
#             word['text'] for word in sorted(line, key=lambda w: w['x0'])
#             if not is_in_table(word, [t.bbox for t in region_tables])
#         )
#         if line_text.strip():
#             avg_top = sum(word['top'] for word in line) / len(line)
#             elements.append({"type": "text", "top": avg_top, "content": line_text.strip()})

#     for table in region_tables:
#         cleaned_table = [
#             [cell.strip() if cell else "" for cell in row]
#             for row in table.extract()
#         ]
#         elements.append({"type": "table", "top": table.bbox[1], "content": cleaned_table})

#     # 위치 기준 정렬
#     elements.sort(key=lambda e: e['top'])
#     return elements


# def extract_page_elements(page):
#     page_width = page.width
#     words = page.extract_words()
#     tables = page.find_tables()

#     # x축 기준 좌/우로 나누기
#     word_left, word_right = split_by_half_x(words, page_width, key=lambda w: w['x0'])
#     table_left, table_right = split_by_half_x(tables, page_width, key=lambda t: t.bbox[0])

#     # 각각 왼쪽, 오른쪽 영역 처리
#     left_elements = process_region(word_left, table_left)
#     right_elements = process_region(word_right, table_right)

#     return [left_elements, right_elements]


# def extract_text_and_tables_to_txt(pdf_path: str, save_dir: str) -> str:
#     os.makedirs(os.path.dirname(save_dir), exist_ok=True)
#     print(pdf_path)
#     for filename in os.listdir(pdf_path):
#         if pdf_path.lower().endswith('.pdf'):
            
#             output_file_path = os.path.join(save_dir, f"{os.path.splitext(filename)[0]}_pyplumber_pixpos.json.txt")
#             full_text = ""

#             with open(output_file_path, "w", encoding="utf-8-sig") as f_out:
#                 with pdfplumber.open(pdf_path) as pdf:
#                     for page_number, page in enumerate(pdf.pages, start=1):
#                         elements = extract_page_elements(page)
                        
#                         for region_elements in elements:
#                             for el in region_elements:
#                                 if el["type"] == "text":
#                                     f_out.write(el["content"] + "\n")
#                                     full_text += el["content"] + "\n"
#                                 elif el["type"] == "table":
#                                     table_json = json.dumps({"table": el["content"]}, ensure_ascii=False)
#                                     f_out.write(table_json + "\n")
#                                     full_text += table_json + "\n"
#                             f_out.write("\n\n")
#                             full_text += "\n\n"

#             print(f"✅ TXT 파일 저장 완료: {output_file_path}")
#             return full_text


# # --- Step 4: 줄(line) 기준 그룹핑 ---
# def group_words_by_line(words, line_threshold=3):
#     lines = []
#     current_line = []
#     current_y = None

#     for word in sorted(words, key=lambda w: (w['top'], w['x0'])):
#         if current_y is None or abs(word['top'] - current_y) <= line_threshold:
#             current_line.append(word)
#             current_y = word['top']
#         else:
#             lines.append(current_line)
#             current_line = [word]
#             current_y = word['top']

#     if current_line:
#         lines.append(current_line)

#     return lines

# # --- Step 4: 전체 파일 로딩 및 처리 ---
# def load_pdf2txt_dataset(data_path, save_path):

#     for filename in os.listdir(data_path):
#         if filename.lower().endswith(".pdf"):  # PDF 파일만 처리
#             file_path = os.path.join(data_path, filename)
#             file_name_without_ext = os.path.splitext(os.path.basename(file_path))[0]

#             data_json = extract_text_and_tables_to_txt(
#                 pdf_path = file_path,
#                 save_dir = save_path
#             )
#     return data_json

# # --- Step 1: JSON Table을 Markdown 형식으로 변환 ---
# def table_json_to_markdown(table_json):
#     if not table_json or not any(table_json):
#         return ""

#     cleaned_table = []
#     for row in table_json:
#         cleaned_row = [re.sub(r"\s*\n\s*", " ", cell.strip()) if cell else "" for cell in row]
#         cleaned_table.append(cleaned_row)

#     header = "| " + " | ".join(cleaned_table[0]) + " |"
#     separator = "| " + " | ".join(["---"] * len(cleaned_table[0])) + " |"
#     rows = ["| " + " | ".join(row) + " |" for row in cleaned_table[1:]]

#     return "\n".join([header, separator] + rows)

# # --- Step 2: 텍스트와 표를 구분해서 Chunking ---
# def text_and_tables(document: str):
#     chunks = []
#     buffer = ""

#     lines = document.splitlines()

#     for line in lines:
#         line = line.strip()

#         if line.startswith("{\"table\":"):
#             if buffer.strip():
#                 chunks.append(buffer.strip())
#                 buffer = ""

#             try:
#                 table_data = json.loads(line)
#                 table_md = table_json_to_markdown(table_data["table"])
#                 chunks.append(table_md)
#             except json.JSONDecodeError:
#                 print("⚠️ 잘못된 테이블 JSON:", line)

#         else:
#             buffer += line + " "

#     if buffer.strip():
#         chunks.append(buffer.strip())

#     return chunks


# def test_pyplumber_pixpos(data_path, save_path):
#     # 저장 경로가 존재하지 않으면 생성
#     os.makedirs(save_path, exist_ok=True)

#     for filename in os.listdir(data_path):
#         if filename.lower().endswith('.pdf'):
                    
#             # PDF → 텍스트+표 추출 → 텍스트 반환
#             data_json = load_pdf2txt_dataset(data_path, save_path)
#             # 표는 Markdown으로 변환, 텍스트는 그대로 유지
#             data_markdown = text_and_tables(data_json)
            
#             print(data_markdown)
#             full_text = "\n\n".join(data_markdown)
            
#             output_file_path = os.path.join(save_path, f"{os.path.splitext(filename)[0]}_pyplumber_pixpos.markdown.txt")


#             with open(output_file_path, 'w', encoding='utf-8') as fp:
#                 fp.write(full_text)

#             print(f"✅ Markdown 저장 완료: {output_file_path}")
