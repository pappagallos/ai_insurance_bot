"""
Create hierarchical_data by parsing HTML

Created on 2025-05-21 by Seungwoon Shin

Note:
     
"""


import json
import os
import re
from bs4 import BeautifulSoup




def find_toc_section(soup):
    """목차 섹션 찾기 함수"""
    # 1. "목차", "차례" 등의 텍스트를 포함하는 제목 찾기
    toc_heading = soup.find(['h1', 'h2', 'h3'], string=lambda s: s and ('목차' in s or '차례' in s))
    if toc_heading:
        # 목차 제목 다음 요소부터 다음 제목까지를 목차 섹션으로 간주
        toc_section = []
        current = toc_heading.next_sibling
        while current and not (current.name in ['h1', 'h2', 'h3'] if current.name else False):
            toc_section.append(current)
            current = current.next_sibling
        return toc_section
    
    # 2. 목차 특성을 가진 div 찾기 (예: 숫자와 제목이 반복되는 패턴)
    divs = soup.find_all('div')
    for div in divs:
        text = div.get_text()
        # 목차 패턴 확인 (예: "1. 제목" 패턴이 여러 줄)
        if re.search(r'\d+\.\s+.+\n\d+\.\s+.+', text):
            return div
    
    return None

def extract_toc_sections(toc_element):
    """목차에서 섹션 추출 함수"""
    sections = []
    
    # 목차 요소의 유형에 따라 처리
    if isinstance(toc_element, list):
        # 요소 목록인 경우
        toc_text = ''.join([str(elem) for elem in toc_element])
        soup = BeautifulSoup(toc_text, 'html.parser')
        toc_text = soup.get_text()
    else:
        # 단일 요소인 경우
        toc_text = toc_element.get_text()
    
    # 정규식으로 목차 항목 추출
    section_pattern = r'(\d+)\.?\s+([^\n]+)'
    matches = re.findall(section_pattern, toc_text)
    
    for match in matches:
        section_num, section_title = match
        sections.append({
            'number': section_num,
            'title': section_title.strip()
        })
    
    return sections

def extract_content_for_sections(soup, hierarchy):
    """섹션에 콘텐츠 추출 및 추가하는 함수"""
    # 현재 처리 중인 섹션 정보
    current_l1 = None
    current_l2 = None
    current_l3 = None
    
    # 모든 요소를 순회하며 콘텐츠 추출
    for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'div', 'span'], recursive=True):
        # 헤딩 태그인 경우 현재 섹션 업데이트
        if element.name in ['h1', 'h2', 'h3']:
            level = int(element.name[1])
            title = element.get_text().strip()
            
            if level == 1:
                # 이미 계층 구조에 있는 제목인지 확인
                for section_title in hierarchy.keys():
                    if title.lower() in section_title.lower() or section_title.lower() in title.lower():
                        current_l1 = section_title
                        current_l2 = None
                        current_l3 = None
                        break
                else:
                    # 일치하는 제목이 없으면 새로 추가
                    current_l1 = title
                    hierarchy[current_l1] = {'subsections': {}, 'content': []}
                    current_l2 = None
                    current_l3 = None
            
            elif level == 2 and current_l1:
                # L2 섹션 업데이트
                current_l2 = title
                if 'subsections' not in hierarchy[current_l1]:
                    hierarchy[current_l1]['subsections'] = {}
                if current_l2 not in hierarchy[current_l1]['subsections']:
                    hierarchy[current_l1]['subsections'][current_l2] = {'content': []}
                current_l3 = None
            
            elif level == 3 and current_l1 and current_l2:
                # L3 섹션 업데이트
                current_l3 = title
                if 'subsections' not in hierarchy[current_l1]['subsections'][current_l2]:
                    hierarchy[current_l1]['subsections'][current_l2]['subsections'] = {}
                if current_l3 not in hierarchy[current_l1]['subsections'][current_l2]['subsections']:
                    hierarchy[current_l1]['subsections'][current_l2]['subsections'][current_l3] = {'content': []}
        
        # 일반 텍스트 콘텐츠인 경우 현재 섹션에 추가
        elif element.name in ['p', 'div', 'span'] and not element.find_parent('table'):
            content = element.get_text().strip()
            if not content:  # 빈 내용 건너뛰기
                continue
            
            # 표가 아닌 일반 텍스트 콘텐츠 추가
            if current_l3 and current_l2 and current_l1:
                hierarchy[current_l1]['subsections'][current_l2]['subsections'][current_l3]['content'].append(content)
            elif current_l2 and current_l1:
                hierarchy[current_l1]['subsections'][current_l2]['content'].append(content)
            elif current_l1:
                hierarchy[current_l1]['content'].append(content)


def is_meaningful_empty_row(row_data):
    """셀 병합이 있는 경우 의미 있는 행으로 간주"""
    if any(cell['rowspan'] > 1 or cell['colspan'] > 1 for cell in row_data):
        return True
    return False

def is_meaningful_empty_cell(cell, row):
    """의미 있는 빈 셀인지 판단하는 함수"""
    # 1. 셀 병합이 있는 경우
    if cell['rowspan'] > 1 or cell['colspan'] > 1:
        return True
    return False

def determine_table_section(table, hierarchy):
    """표가 속한 섹션을 결정하는 함수"""
    # 표의 위치를 기반으로 소속 섹션 결정
    section_info = {
        'l1': None,
        'l2': None,
        'l3': None,
        'level': 0
    }
    
    # 표의 이전 요소들을 확인하여 가장 가까운 헤딩 찾기
    prev_element = table.previous_element
    
    # 이전 요소를 거슬러 올라가며 헤딩 태그 찾기
    while prev_element:
        if prev_element.name in ['h1', 'h2', 'h3']:
            level = int(prev_element.name[1])
            title = prev_element.get_text().strip()
            
            # 찾은 헤딩이 계층 구조에 있는지 확인
            if level == 1:
                for section_title in hierarchy.keys():
                    if title.lower() in section_title.lower() or section_title.lower() in title.lower():
                        section_info['l1'] = section_title
                        section_info['level'] = 1
                        break
            elif level == 2 and section_info['l1']:
                for subsection_title in hierarchy[section_info['l1']]['subsections'].keys():
                    if title.lower() in subsection_title.lower() or subsection_title.lower() in title.lower():
                        section_info['l2'] = subsection_title
                        section_info['level'] = 2
                        break
            elif level == 3 and section_info['l1'] and section_info['l2']:
                for subsubsection_title in hierarchy[section_info['l1']]['subsections'][section_info['l2']]['subsections'].keys():
                    if title.lower() in subsubsection_title.lower() or subsubsection_title.lower() in title.lower():
                        section_info['l3'] = subsubsection_title
                        section_info['level'] = 3
                        break
            
            # 가장 가까운 헤딩을 찾았으면 중단
            if section_info['level'] > 0:
                break
        
        prev_element = prev_element.previous_element
    
    # 헤딩을 찾지 못한 경우 문서의 첫 번째 섹션에 할당
    if section_info['level'] == 0 and hierarchy:
        first_section = next(iter(hierarchy))
        section_info['l1'] = first_section
        section_info['level'] = 1
    
    return section_info

def extract_table_data(table):
    """표 데이터 추출 함수"""
    table_data = {
        'headers': [],
        'body_sections': []  # 여러 tbody를 처리하기 위한 구조
    }
    
    # 1. 테이블 헤더 추출
    # thead에서 헤더 찾기
    thead = table.find('thead')
    if thead:
        header_rows = thead.find_all('tr')
        if header_rows:
            # 마지막 헤더 행에서 헤더 텍스트 추출
            headers = header_rows[-1].find_all(['th', 'td'])
            table_data['headers'] = [header.get_text().strip() for header in headers]
            
            # 다중 행 헤더인 경우 추가 정보 저장
            if len(header_rows) > 1:
                table_data['multi_row_headers'] = []
                for row in header_rows[:-1]:
                    header_cells = row.find_all(['th', 'td'])
                    table_data['multi_row_headers'].append([{
                        'text': cell.get_text().strip(),
                        'colspan': int(cell.get('colspan', 1)),
                        'rowspan': int(cell.get('rowspan', 1))
                    } for cell in header_cells])
    
    # thead가 없는 경우 첫 번째 행을 헤더로 사용
    if not table_data['headers']:
        first_row = table.find('tr')
        if first_row:
            headers = first_row.find_all(['th', 'td'])
            table_data['headers'] = [header.get_text().strip() for header in headers]
    
    # 2. 테이블 본문 데이터 추출
    # 모든 tbody 요소 찾기
    tbodies = table.find_all('tbody')
    
    # tbody가 명시적으로 있는 경우
    if tbodies:
        for tbody_idx, tbody in enumerate(tbodies):
            body_section = {
                'section_index': tbody_idx,
                'rows': []
            }
            
            # tbody에서 클래스나 ID가 있으면 섹션 이름으로 사용
            if tbody.get('class'):
                body_section['section_name'] = ' '.join(tbody.get('class'))
            elif tbody.get('id'):
                body_section['section_name'] = tbody.get('id')
            
            # tbody 내의 모든 행 처리
            rows = tbody.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if cells:
                    # 셀 데이터 추출 (텍스트 및 속성)
                    row_data = []
                    for cell in cells:
                        cell_text = cell.get_text().strip()
                        cell_data = {
                            'text': cell_text,
                            'rowspan': int(cell.get('rowspan', 1)),
                            'colspan': int(cell.get('colspan', 1)),
                            'is_empty': cell_text == ""
                        }
                        # 셀에 클래스가 있으면 추가
                        if cell.get('class'):
                            cell_data['class'] = ' '.join(cell.get('class'))
                        row_data.append(cell_data)

                    # 빈 행 여부 확인 (모든 셀이 빈 경우)
                    is_empty_row = all(cell['is_empty'] for cell in row_data)
                    if not is_empty_row or is_meaningful_empty_row(row_data):                      
                        body_section['rows'].append(row_data)
        if body_section['rows']:    
            table_data['body_sections'].append(body_section)
    else:
        # tbody가 명시적으로 없는 경우
        body_section = {
            'section_index': 0,
            'rows': []
        }
        
        # 테이블의 모든 행 처리 (헤더 행 제외)
        rows = table.find_all('tr')
        start_idx = 1 if table_data['headers'] else 0
        
        for row in rows[start_idx:]:
            cells = row.find_all(['td', 'th'])
            if cells:
                row_data = []
                for cell in cells:
                    cell_data = {
                        'text': cell.get_text().strip(),
                        'rowspan': int(cell.get('rowspan', 1)),
                        'colspan': int(cell.get('colspan', 1))
                    }
                    if cell.get('class'):
                        cell_data['class'] = ' '.join(cell.get('class'))
                    row_data.append(cell_data)
                body_section['rows'].append(row_data)
        
        table_data['body_sections'].append(body_section)
    
    # 3. 테이블 푸터 추출 (있는 경우)
    tfoot = table.find('tfoot')
    if tfoot:
        footer_rows = tfoot.find_all('tr')
        if footer_rows:
            table_data['footer'] = []
            for row in footer_rows:
                cells = row.find_all(['td', 'th'])
                table_data['footer'].append([cell.get_text().strip() for cell in cells])
    
    # 4. 간소화된 데이터 형식도 제공 (기존 형식과의 호환성)
    # 모든 본문 섹션의 행을 하나의 리스트로 병합
    all_rows = []
    for section in table_data['body_sections']:
        for row in section['rows']:
            # 빈 셀이 아닌 셀만 포함하거나, 의미 있는 빈 셀은 유지
            filtered_row = []
            for cell in row:
                if is_meaningful_empty_cell(cell, row):
                    filtered_row.append(cell['text'])
                else:
                    # 빈 셀이지만 구조적으로 필요한 경우 빈 문자열 유지
                    filtered_row.append("")
            # 모든 셀이 빈 문자열이 아닌 경우만 추가
            if any(text != "" for text in filtered_row):
                all_rows.append(filtered_row)
    table_data['rows'] = all_rows
    return table_data


def extract_tables_for_sections(soup, hierarchy):
    tables = soup.find_all('table')
    
    for table in tables:
        # 표의 위치를 기반으로 소속 섹션 결정
        section_info = determine_table_section(table, hierarchy)
        
        # 표 데이터 추출
        table_data = extract_table_data(table)
        
        # 표 캡션 추출 (있는 경우)
        caption = table.find('caption')
        if caption:
            table_data['caption'] = caption.get_text().strip()
        
        # 계층 구조에 표 데이터 추가
        if section_info['level'] == 1:
            if 'tables' not in hierarchy[section_info['l1']]:
                hierarchy[section_info['l1']]['tables'] = []
            hierarchy[section_info['l1']]['tables'].append(table_data)
        elif section_info['level'] == 2:
            if 'tables' not in hierarchy[section_info['l1']]['subsections'][section_info['l2']]:
                hierarchy[section_info['l1']]['subsections'][section_info['l2']]['tables'] = []
            hierarchy[section_info['l1']]['subsections'][section_info['l2']]['tables'].append(table_data)
        elif section_info['level'] == 3:
            if 'tables' not in hierarchy[section_info['l1']]['subsections'][section_info['l2']]['subsections'][section_info['l3']]:
                hierarchy[section_info['l1']]['subsections'][section_info['l2']]['subsections'][section_info['l3']]['tables'] = []
            hierarchy[section_info['l1']]['subsections'][section_info['l2']]['subsections'][section_info['l3']]['tables'].append(table_data)


def has_hierarchical_headers(table):
    """계층적 헤더 확인 함수"""
    # 다중 행 헤더가 있는지 확인
    thead = table.find('thead')
    if thead:
        rows = thead.find_all('tr')
        return len(rows) > 1
    
    # thead가 없는 경우, 첫 두 행을 확인
    rows = table.find_all('tr')
    if len(rows) >= 2:
        first_row_cells = rows[0].find_all(['th', 'td'])
        second_row_cells = rows[1].find_all(['th', 'td'])
        
        # 첫 번째 행에 colspan이 있거나 두 번째 행에 th가 있으면 계층적 헤더로 간주
        for cell in first_row_cells:
            if cell.get('colspan') and int(cell.get('colspan')) > 1:
                return True
        
        for cell in second_row_cells:
            if cell.name == 'th':
                return True
    
    return False


def extract_hierarchical_headers(table):
    """계층적 헤더 추출 함수"""
    hierarchical_headers = []
    
    # thead에서 행 추출
    thead = table.find('thead')
    if thead:
        rows = thead.find_all('tr')
    else:
        # thead가 없으면 첫 두 행을 사용
        rows = table.find_all('tr')[:2]
    
    # 각 행의 헤더 추출
    for row_idx, row in enumerate(rows):
        header_row = []
        cells = row.find_all(['th', 'td'])
        
        for cell in cells:
            cell_text = cell.get_text().strip()
            rowspan = int(cell.get('rowspan', 1))
            colspan = int(cell.get('colspan', 1))
            
            header_cell = {
                'text': cell_text,
                'rowspan': rowspan,
                'colspan': colspan,
                'row': row_idx
            }
            header_row.append(header_cell)
        hierarchical_headers.append(header_row)
    return hierarchical_headers


def extract_hierarchical_structure(soup):
    """계층적 구조 추출 함수"""
    hierarchy = {}
    
    # 목차 섹션 찾기 (예: 특정 제목이나 클래스로 식별)
    toc_section = soup.find('div', class_='toc') or find_toc_section(soup)
    
    # 목차에서 주요 섹션 추출
    if toc_section:
        main_sections = extract_toc_sections(toc_section)
        
        # 목차 기반으로 계층 구조 초기화
        for section in main_sections:
            hierarchy[section['title']] = {'subsections': {}, 'content': []}
    
    # 헤딩 태그를 기반으로 계층 구조 생성
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    current_l1 = None
    current_l2 = None
    current_l3 = None
    
    for heading in headings:
        level = int(heading.name[1])  # h1 -> 1, h2 -> 2, ...
        title = heading.get_text().strip()
        
        if level == 1:
            current_l1 = title
            if current_l1 not in hierarchy:
                hierarchy[current_l1] = {'subsections': {}, 'content': []}
            current_l2 = None
            current_l3 = None
        elif level == 2 and current_l1:
            current_l2 = title
            if 'subsections' not in hierarchy[current_l1]:
                hierarchy[current_l1]['subsections'] = {}
            hierarchy[current_l1]['subsections'][current_l2] = {'content': []}
            current_l3 = None
        elif level == 3 and current_l1 and current_l2:
            current_l3 = title
            if 'subsections' not in hierarchy[current_l1]['subsections'][current_l2]:
                hierarchy[current_l1]['subsections'][current_l2]['subsections'] = {}
            hierarchy[current_l1]['subsections'][current_l2]['subsections'][current_l3] = {'content': []}
    
    # 콘텐츠 추출 및 계층 구조에 추가
    extract_content_for_sections(soup, hierarchy)
    
    # 표 추출 및 계층 구조에 추가
    extract_tables_for_sections(soup, hierarchy)
    
    return hierarchy


def organizer():
    """ Do all process """
    if not os.path.exists("hierarchical_data"):
        os.makedirs("hierarchical_data")
    org_jsons = [f for f in os.listdir() if f.endswith('.json')]


    for org_json in org_jsons:
        with open(org_json, "r", encoding="utf-8") as f:
            json_file = json.load(f)
        soup = BeautifulSoup(json_file, 'html.parser')
        hierarchical_data = extract_hierarchical_structure(soup)
        with open(f"hierarchical_data/{org_json[:-9]}.json", "w", encoding="utf-8") as f:
            json.dump(hierarchical_data, f, ensure_ascii=False, indent=2)



if __name__ == '__main__':
    organizer()
