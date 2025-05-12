from test_pyplumber_pixpos import test_pyplumber_pixpos
from test_pymupdf4llm import test_pymupdf4llm
from test_pdf2html_beautifulsoup import test_pdf2html_beautifulsoup
# from test_donut_ocr import test_donut_ocr # 성능 안나옴


if __name__ == "__main__":
    data_path = "./data"
    save_path = "./output"
    
    test_pymupdf4llm(data_path, save_path)
    print(f"✅ test_pymupdf4llm 저장 완료: {save_path}")
    
    test_pdf2html_beautifulsoup(data_path, save_path)
    print(f"✅ test_pdf2html_beautifulsoup 저장 완료: {save_path}")
    
    test_pyplumber_pixpos(data_path, save_path)
    print(f"✅ test_pyplumber_pixpos 저장 완료: {save_path}")