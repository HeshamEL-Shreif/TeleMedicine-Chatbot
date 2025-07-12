# 🧠 TeleMedicine Chatbot – Backend (FastAPI + LangGraph)

This repository combines two major components:

### 📌 1. Preprocessing & OCR Pipeline  
A script that automates the scraping and transformation of public Arabic and English medical documents into structured PDF files:
- 🌐 Scrapes images from a public Google Sites portal for patient education
- 🧠 Extracts Arabic text using a Vision-Language Qwen2 model
- 🔠 Extracts English text using Tesseract OCR
- 🗃 Merges extracted text and saves them as `.txt` files
- 🧾 Converts all text into **properly aligned Arabic-friendly PDFs** using ReportLab

### 🚀 2. Multilingual AI Chatbot Backend  
A FastAPI server that supports Arabic-English medical queries using Retrieval-Augmented Generation (RAG) with Groq’s LLaMA 4 model, LangGraph agents, and web search tools.

---

## 🩺 Features

- 🔍 Medical QA with Retrieval-Augmented Generation (RAG)  
- 🌐 Arabic & English support with dynamic language detection  
- 📑 Synthetic paragraph generation for semantic document search  
- 🛠 LangGraph agent for smart tool use & reasoning  
- 📚 Persistent document storage in Chroma vector DB  
- 🌐 Web augmentation using Tavily API  
- 🚀 FastAPI server with an intuitive REST endpoint  
- 🐳 Docker-ready for fast deployment  
- 🖼 Preprocessing pipeline that scrapes medical image content and prepares structured PDF datasets  

---

## 🗂 Project Structure

```bash
.
├── data/
│   ├── downloaded_images_Ar/       # Arabic scraped images and extracted text
│   ├── downloaded_images_En/       # English scraped images and extracted text
│   ├── Amiri-Regular.ttf           # Arabic-capable font for PDF generation
│   └── scraper_ocr_pipeline.py     # Google Sites scraper + OCR extractor + PDF builder
├── db/                            # Vector DB logic (Chroma)
│   └── vector_db.py
├── documents/                    # Auto-generated PDFs from extracted medical content
├── utils/
│   └── utils.py                  # LLM and search tool logic
├── retrieve.py                   # Generates synthetic Arabic documents
├── agent.py                      # LangGraph agent workflow
├── main.py                       # FastAPI app with /query endpoint
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🧠 LLM & Tools

| Component        | Model/Tool                                                                 |
|------------------|-----------------------------------------------------------------------------|
| LLM              | `meta-llama/llama-4-scout-17b-16e-instruct` via Groq API                    |
| Arabic OCR       | `NAMAA-Space/Qari-OCR-0.1-VL-2B-Instruct`                                   |
| Embeddings       | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`               |
| English OCR      | Tesseract (`pytesseract`)                                                   |
| Search API       | Tavily                                                                       |
| RAG Agent        | LangGraph                                                                   |

---

## 🧪 Example API Call

**Endpoint:** `POST /query`  
**Request:**
```json
{
  "query": "ما هو دواء الداكتون؟"
}
```
**Response:**
```json
{
  "answer": "الداكتون (سبيرونولاكتون) هو دواء مدر للبول يحافظ على البوتاسيوم ويستخدم لعلاج احتباس السوائل الناتج عن أمراض القلب والكبد والكلى..."
}
```

---

## 🧰 Setup Instructions

### 1. Clone the Repo
```bash
git clone https://github.com/yourusername/telemedicine-chatbot-backend.git
cd telemedicine-chatbot-backend
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys in `.env`
```
TAVILY_API_KEY=your_api_key_here
HUGGINGFACEHUB_API_TOKEN=your_api_key_here
GROQ_API_KEY=your_api_key_here
```

---

## 🧪 Run the Backend API

```bash
uvicorn main:app --reload
```
Access docs at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🖼 Run the Scraper + OCR Pipeline

The pipeline is already integrated into `scraper_ocr_pipeline.py`.

To run it:
```bash
python ./data/scraper_ocr_pipeline.py
```

This will:
- Scrape the main Google Sites medical portal
- Save Arabic & English images under respective folders
- Extract and save `.txt` files from images
- Generate properly formatted PDFs into the `documents/` folder

---

## 🐳 Docker Usage

### Build the Image
```bash
docker build -t telemedicine-backend .
```

### Run the Container
```bash
docker run -p 8000:8000 telemedicine-backend
```

---

## 🧠 How It Works
1.	User query is received.
2.	Query is language detected (Arabic or English).
3.	A synthetic paragraph is generated using LLM to simulate an answer-containing doc.
4.	Similarity search runs on that paragraph against internal medical vector DB.
5.	Web search snippets are fetched via Tavily (if relevant).
6.	LangGraph agent uses tools + context to generate a final answer.
7.	Final answer is returned in the user’s language, avoiding direct quoting.

---

## 🧠 Prompt Logic Highlights
- Responds only with medical facts
- Ignores or filters non-medical questions
- Detects and replies in the user’s language
- Prefers internal documents, then supplements with web content
- Avoids hallucinations and general-purpose LLM errors