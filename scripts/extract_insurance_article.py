import re
import argparse
from pypdf import PdfReader


parser = argparse.ArgumentParser()
parser.add_argument("--insurance_name", type=str, required=True)
parser.add_argument("--file", type=str, required=True)
parser.add_argument("--start_page", type=int, required=True)
parser.add_argument("--end_page", type=int, required=True)

args = parser.parse_args()
insurance_name = args.insurance_name
file_path = args.file
start_page = args.start_page
end_page = args.end_page


INDEX_START_PATTERN = re.compile(r"^\s*제\s*\d+\s*[관조]")
INDEX_END_PATTERN = re.compile(r"\s*\d+\s$")

REPLACE_WHITESPACE = re.compile(r"[\s\n]+")

EXTRACT_INDEX = re.compile(r"제\s*\d+\s*[관조]\s*【?[\s\w\‘\’\,\'\(\)\:\-]+】?\s\d{1,3}\s*|제\s*\d+\s*조의\d{1,2}\s*【?[\s\w\‘\’\,\'\(\)\:\-]+】?\s\d{1,3}\s*")
EXTRACT_ARTICLE = re.compile(r"(제\s*\d+\s*[관조])(【?[\s\w\‘\’\,\'\(\)\:\-]+】?)\s(\d+)")
EXTRACT_ARTICLE_WITH_CHAPTER = re.compile(r"(제\s*\d+\s*조의\s*\d{1,2})(【?[\s\w\‘\’\,\'\(\)\:\-]+】?)\s(\d+)")

EXCLUDE_INDEX = re.compile(r"^\s*제\s*\d+조\s*\(|제\s\d+\s$|취급방침|제\d+호")


def read_pdf(file_path: str) -> str:
    """
    PDF 파일 읽기 함수
    """
    reader = PdfReader(file_path)
    text = ""
    pages = reader.pages
    for page in pages:
        text += page.extract_text()
    return (text, pages, pages[start_page-1:end_page+1])


def extract_index(text: str) -> str:
    """
    목차 추출 함수
    """
    text = REPLACE_WHITESPACE.sub(" ", text)
    text = re.sub(r"\】(\d+)", r"】 \1", text)
    return EXTRACT_INDEX.findall(text)


def filter_index(index: list[str]) -> list[str]:
    """
    목차 필터링 함수
    """
    # 실제 목차만 필터링하는 추가 로직
    filtered_index = []
    for item in index:
        # 목차 형식 검증, 제[0-9]+관 또는 제[0-9]+조로 시작하고 숫자로 끝나는지
        if INDEX_START_PATTERN.search(item) is None or INDEX_END_PATTERN.search(item) is None:
            continue
        
        # "제[0-9]+조"로 시작하고 "("로 시작하는 목차 제거, "제 [0-9]+" 으로 끝나는 목차 제거
        if EXCLUDE_INDEX.search(item):
            continue

        filtered_index.append(item.strip())
    return filtered_index


def get_article_from_index(index: list[str], text: str) -> list[str]:
    """
    목차 조문, 페이지 추출 함수
    """
    articles = []
    for item in index:
        if match := EXTRACT_ARTICLE.match(item):
            articles.append((f"{match[1]} {match[2].replace('【', '').replace('】', '').strip()}", match[3]))
        elif match := EXTRACT_ARTICLE_WITH_CHAPTER.match(item):
            articles.append((f"{match[1]} {match[2].replace('【', '').replace('】', '').strip()}", match[3]))
    return articles


def process_index(text: str) -> list[str]:
    """
    목차 처리 함수
    """
    index = extract_index(text)
    filtered_index = filter_index(index)
    return get_article_from_index(filtered_index, text)


text, total_pages, filted_pages = read_pdf(file_path)


page_indexes = process_index(text)
print(page_indexes, len(page_indexes))

# print(extract_insurance_article(file_path))

# python3 extract_insurance_article.py --insurance_name "369뉴테크NH암보험 |무배당|_2404 주계약 약관" --file "/Users/woojinlee/Desktop/ai_insurance_bot/김백현_농협생명보험_흥국생명보험_KB라이프생명보험/농협생명보험/369뉴테크NH암보험(무배당)/저용량-369뉴테크NH암보험(무배당)_2404_최종_241220.pdf" --start_page 45 --end_page 103
