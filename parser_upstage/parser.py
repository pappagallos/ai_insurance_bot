"""
UpstageParser from pdf to HTML.json.

Created on 2025-05-19 by Seungwoon Shin

Note:
     Upstage API key(UPSTAGE_API_KEY), data folder required.
"""

from dotenv import load_dotenv
load_dotenv(dotenv_path="../insurance_chat_backend_fastapi/")

from langchain_upstage import UpstageDocumentParseLoader
from dataclasses import dataclass
import fitz
import glob
import json
import os

@dataclass
class UpstageParser:
    """
    UpstageParser from pdf to HTML.json

    Args:
        input_dir: input directory to split
        save_dir: save directory for splited pdf
        split_size: maximum capacity that Upstage parser can handle is 30
    """
    input_dir: str = "data"
    save_dir: str = "splited_data"
    split_size: int = 30


    def split_pdf(self, org_pdf):
        """ Split pdf files to fit upstage parser 
        
        Args:
            org_pdf: target pdf file directory
        """
        full_path = os.path.join(self.input_dir, org_pdf)
        input_pdf = fitz.open(full_path)
        num_pages = len(input_pdf)
        num_pdf = 0
        print(f"Total number of pages: {num_pages}")

        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
        for start_page in range(0, num_pages, self.split_size):
            num_pdf += 1
            end_page = min(start_page + self.split_size, num_pages) - 1
    
            input_dir_filename = os.path.splitext(org_pdf)[0]        
            output_file = f"{self.save_dir}/{input_dir_filename}_{num_pdf}.pdf"
            print(output_file)
            with fitz.open() as output_pdf:
                output_pdf.insert_pdf(input_pdf, from_page=start_page, to_page=end_page)
                output_pdf.save(output_file)
    
        input_pdf.close()


    @property 
    def parsing(self):
        """Extract pdf files as a HTML.json form"""
        org_pdfs = [f for f in os.listdir(self.input_dir) if f.endswith('.pdf')]

        if len(os.listdir(self.input_dir)) >= 5:
            for org_pdf in org_pdfs:
                self.split_pdf(org_pdf)

        for pdf_file in org_pdfs:
            if os.path.exists(f"{pdf_file}.json"):
                continue
            
            file_name = pdf_file[:-4]
            pdf_pattern = f"{self.save_dir}/{file_name}_*.pdf"
            matching_files = glob.glob(pdf_pattern)
            file_count = len(matching_files)
            file_paths = [f"{self.save_dir}/{file_name}_{i}.pdf" for i in range(1, file_count+1)]

            all_html_content = []
            for file_path in file_paths:
                loader = UpstageDocumentParseLoader(
                    file_path,
                    split="none",  # 분할하지 않고 전체 문서 구조 유지
                    output_format="html",  # HTML 형식으로 출력
                    api_key=os.getenv('UPSTAGE_API_KEY'),
                    coordinates=True,  # 좌표 정보 포함
                    ocr="auto"  # 필요시 OCR 자동 적용
                )
                docs = loader.load()                

                for doc in docs:
                    all_html_content.append(doc.page_content)

            combined_html = "\n".join(all_html_content)
            with open(f"{pdf_file}.json", "w", encoding="utf-8") as f:
                json.dump(combined_html, f, ensure_ascii=False, indent=2)
                print(f"{pdf_file}.json file saved")
        print("UpstageParsing Completed")

if __name__ == '__main__':
    UpstageParser().parsing
    
