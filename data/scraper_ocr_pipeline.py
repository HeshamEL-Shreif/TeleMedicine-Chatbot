
## This script scrapes a Google Sites page for links to documents, downloads images, 
## extracts Arabic text using a Qwen2 model, and English text using pytesseract. It then generates PDFs from the extracted text.

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
import uuid
from PIL import Image
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
import torch
import os
from qwen_vl_utils import process_vision_info  # make sure this is in your path
from pathlib import Path
import pytesseract
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from bidi.algorithm import get_display
import arabic_reshaper


######## Scraping data (images) ########
def extract_folder_name(url):
    """
    Given a URL, extract the last segment after /home/
    e.g. 
    https://.../home/foo/bar/baz
    returns 'baz'
    """
    parsed = urlparse(url)
    path = parsed.path
    if "/home/" in path:
        after_home = path.split("/home/")[1]
        segments = after_home.strip("/").split("/")
        folder_name = segments[-1]
        return unquote(folder_name)  # decode %XX if Arabic or other
    return None


def scrape_google_site_images(main_url, base_folder="downloaded_images_Ar"):
    """
    Scrapes image URLs from a Google Sites page and downloads them into folders.

    Args:
        main_url (str): The Google Sites main page URL.
        base_folder (str): Base directory to save downloaded images.
    """
    os.makedirs(base_folder, exist_ok=True)

    response = requests.get(main_url)
    soup = BeautifulSoup(response.text, "html.parser")

    a_tags = soup.find_all("a", class_="fqo2vd")
    page_links = []

    for a in a_tags:
        href = a.get("href")
        if href:
            page_links.append(urljoin(main_url, href))

    print(f"Found {len(page_links)} subpages to scrape.")

    for page in page_links:
        print(f"\nScraping page: {page}")
        try:
            folder_name = extract_folder_name(page)
            if not folder_name:
                print(f"Skipping {page}, could not extract folder name.")
                continue

            folder_path = os.path.join(base_folder, folder_name)
            os.makedirs(folder_path, exist_ok=True)

            page_resp = requests.get(page)
            page_soup = BeautifulSoup(page_resp.text, "html.parser")
            images = page_soup.find_all("img", class_="CENy8b")

            if not images:
                print(f"No images found on {page}")
                continue

            for img in images:
                img_url = img.get("src")
                if img_url:
                    if img_url.startswith("//"):
                        img_url = "https:" + img_url
                    elif img_url.startswith("/"):
                        img_url = urljoin(page, img_url)

                    filename = os.path.join(folder_path, f"{uuid.uuid4().hex}.png")
                    img_data = requests.get(img_url).content
                    with open(filename, "wb") as f:
                        f.write(img_data)
                    print(f"Saved: {filename}")
        except Exception as e:
            print(f"Error scraping {page}: {e}")


######## Arabic Text Extraction ########
def extract_arabic_text():
    # load the model
    model_name = "NAMAA-Space/Qari-OCR-0.1-VL-2B-Instruct"
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto"
    )
    processor = AutoProcessor.from_pretrained(model_name)

    max_tokens = 2000

    # go through all folders under downloaded_images
    base_folder = "./downloaded_images_Ar"

    for folder in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder)
        if not os.path.isdir(folder_path):
            continue

        all_text = []
        images = [f for f in os.listdir(folder_path) if f.endswith(".png")]

        for img_file in images:
            img_path = os.path.join(folder_path, img_file)
            print(f"Processing {img_path}")

            prompt = "Below is the image of one page of a document, as well as some raw textual content that was previously extracted for it. Just return the plain text representation of this document as if you were reading it naturally. Do not hallucinate."

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": f"file://{os.path.abspath(img_path)}"},
                        {"type": "text", "text": prompt},
                    ],
                }
            ]

            text_prompt = processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            image_inputs, video_inputs = process_vision_info(messages)

            inputs = processor(
                text=[text_prompt],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            inputs = inputs.to("cuda")

            with torch.no_grad():
                generated_ids = model.generate(**inputs, max_new_tokens=max_tokens)

            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_text = processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )[0]

            all_text.append(output_text.strip())

        # save a single text file with all extracted text merged
        txt_path = os.path.join(folder_path, f"{folder}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(all_text))

        print(f"Saved combined Arabic text to {txt_path}")


######## English Text Extraction ########

def extract_english_text():
    # go through all folders under downloaded_images_En
    base_folder = "./downloaded_images_En"

    for folder in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder)
        if not os.path.isdir(folder_path):
            continue

        all_text = []
        # get images in the folder
        images = [f for f in os.listdir(folder_path) if f.endswith(".png")]

        for img_file in images:
            img_path = os.path.join(folder_path, img_file)
            print(f"Processing {img_path}")

            img = Image.open(img_path)

            
            output_text = pytesseract.image_to_string(img, lang="eng")

            all_text.append(output_text.strip())

        # write all text to a .txt file (UTF-8)
        txt_path = os.path.join(folder_path, f"{folder}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(all_text))

        print(f"Saved extracted text to {txt_path}")



############ PDF Generation ############

# Register Arabic-capable font
pdfmetrics.registerFont(TTFont("ArabicFont", "Amiri-Regular.ttf"))  # Replace with your font file path if needed

def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()

def write_pdf(text_lines, output_path, title):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    c.setFont("ArabicFont", 14)

    # Set PDF metadata
    c.setTitle(title)
    c.setAuthor("Magdi Yacoub")

    y = height - 40

    for line in text_lines:
        line = line.strip()
        if not line:
            y -= 20
            continue

        reshaped = arabic_reshaper.reshape(line)
        bidi_text = get_display(reshaped)

        if y < 40:
            c.showPage()
            c.setFont("ArabicFont", 14)
            y = height - 40

        c.drawRightString(width - 40, y, bidi_text)
        y -= 20

    c.save()
    print(f"Saved {output_path} (title: {title})")

def txt_to_pdf(txt_file, pdf_file, title):
    lines = read_text_file(txt_file)
    write_pdf(lines, pdf_file, title)

def convert_all_txt_to_pdf(folders):
    output_folder = "../documents" 
    os.makedirs(output_folder, exist_ok=True)  # Create it if not exists

    count = 1
    for folder_path in folders:
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                txt_path = os.path.join(folder_path, filename)
                pdf_filename = f"{count}.pdf"
                pdf_path = os.path.join(output_folder, pdf_filename)
                txt_to_pdf(txt_path, pdf_path, title=filename)
                count += 1


if __name__ == "__main__":
    main_url = "https://sites.google.com/view/patientseducationportal/home/%D8%A3%D8%B6%D8%BA%D8%B7-%D9%87%D9%86%D8%A7-%D9%84%D9%84%D9%85%D8%B9%D9%84%D9%88%D9%85%D8%A7%D8%AA-%D8%A7%D9%84%D8%B7%D8%A8%D9%8A%D9%87?authuser=0"
    scrape_google_site_images(main_url)
    extract_arabic_text()
    extract_english_text()
    folders = ["downloaded_images_Ar", "downloaded_images_En"]  
    convert_all_txt_to_pdf(folders)

