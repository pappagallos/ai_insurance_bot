
import os
from pdf2image import convert_from_path
from PIL import Image
from transformers import DonutProcessor, VisionEncoderDecoderModel
import torch

# 모델과 프로세서 불러오기
processor = DonutProcessor.from_pretrained("naver-clova-ix/donut-base")
model = VisionEncoderDecoderModel.from_pretrained("naver-clova-ix/donut-base")
model.to("cpu")  # CUDA 가능 시 "cuda"

def process_image_with_donut(image_path):
    image = Image.open(image_path).convert("RGB")
    image = image.resize((1920, 2560))
    task_prompt = "<s_cord>"
    inputs = processor(image, task_prompt, return_tensors="pt").to("cpu")
    outputs = model.generate(**inputs, max_length=512)
    
    decoded = processor.batch_decode(outputs, skip_special_tokens=True, clean_up_tokenization_spaces=True)[0]
    
    if decoded.startswith("<s_cord>"):
        decoded = decoded.replace("<s_cord>", "").strip()
    
    return decoded


def convert_pdf_to_donut_txt(pdf_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    images = convert_from_path(pdf_path, dpi=300)

    full_result = []

    for idx, image in enumerate(images):
        image_path = os.path.join(output_dir, f"page_{idx+1}.png")

        if os.path.exists(image_path):
            print(f"⏩ {image_path} 이미 존재하여 건너뜁니다.")
        else:
            image.save(image_path)
            print(f"🔍 {image_path} 이미지 저장 완료")

        result = process_image_with_donut(image_path)
        if not result.strip():
            print(f"⚠️ Page {idx+1}: OCR 결과가 비어 있습니다.")
        else:
            print(f"✅ Page {idx+1}: OCR 완료 → 내용 있음")
        full_result.append(f"## Page {idx+1}\n{result}\n")

    txt_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_donut.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(full_result))

    print(f"✅ OCR 결과 저장 완료: {txt_path}")

    

def test_donut_ocr(data_path, save_path):
    os.makedirs(save_path, exist_ok=True)

    for filename in os.listdir(data_path):
        if filename.endswith(".pdf"):
            full_pdf_path = os.path.join(data_path, filename)
            convert_pdf_to_donut_txt(full_pdf_path, save_path)