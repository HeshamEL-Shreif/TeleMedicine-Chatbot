# 🧠 TeleMedicine Chatbot – Backend (FastAPI + LangGraph)

This repository contains the **FastAPI backend** for a **multilingual AI-powered TeleMedicine Chatbot**. The system uses **LangChain**, **LangGraph**, and **Groq’s LLaMA 4 model** for reasoning over internal medical documents and relevant web data via **Tavily search**.

---

## 🩺 Features

- 🔍 **Medical QA with Retrieval-Augmented Generation (RAG)**
- 🌐 **Arabic & English** support with dynamic language detection
- 📑 **Synthetic paragraph generation** for document-based semantic search
- 🛠 **LangGraph agent** for tool selection and reasoning
- 📚 **Chroma vector store** for persistent document storage
- 🌐 **Web search integration** via Tavily
- 🚀 **FastAPI server** with a clean REST endpoint
- 🐳 **Docker-ready** for deployment

---

## 📁 Project Structure

```bash
.
├── db/                            # Vector DB logic (Chroma)
│   └── vector_db.py
├── documents/                    # Your internal medical PDFs
├── utils/
│   └── utils.py                  # llm and search_tool definitions
├── retrieve.py                   # Tool that generates synthetic Arabic text
├── agent.py                      # LangGraph workflow agent
├── main.py                       # FastAPI app with /query endpoint
├── requirements.txt
├── Dockerfile
└── README.md
```
## 🧠 LLM & Tools
- LLM: meta-llama/llama-4-scout-17b-16e-instruct (served by Groq)
- Embedding Model: sentence-transformers paraphrase-multilingual-MiniLM-L12-v2
- Search Tool: Tavily API
- RAG Workflow: Powered by LangGraph

## 🧪 Example API Call

- Endpoint: POST /query

### Request

```json
{
  "query": "ما هو دواء الداكتون؟"
}
```

### Response

```json
{
  "answer": "الداكتون (سبيرونولاكتون) هو دواء مدر للبول يحافظ على البوتاسيوم ويستخدم لعلاج احتباس السوائل الناتج عن أمراض القلب والكبد والكلى..."
}
```

## 🧰 Setup Instructions

1. Clone the Repo
```bash
git clone https://github.com/yourusername/telemedicine-chatbot-backend.git
cd telemedicine-chatbot-backend
```
2. Install Dependencies
```bash
pip install -r requirements.txt
```
3. Create a .env file and add:
```bash
TAVILY_API_KEY=your_api_key_here
HUGGINGFACEHUB_API_TOKEN =your_api_key_here
GROQ_API_KEY=your_api_key_here
```
4. Run the API
```bash
uvicorn main:app --reload
```
5. Visit API docs: http://localhost:8000/docs

## 🐳 Docker Usage
1. Build Docker Image
```bash
docker build -t telemedicine-backend .
```
2. Run the Container
```bash
docker run -p 8000:8000 telemedicine-backend
```

## 🧠 How It Works
1.	User query is received.
2.	Query is language detected (Arabic or English).
3.	A synthetic paragraph is generated using LLM to simulate an answer-containing doc.
4.	Similarity search runs on that paragraph against internal medical vector DB.
5.	Web search snippets are fetched via Tavily (if relevant).
6.	LangGraph agent uses tools + context to generate a final answer.
7.	Final answer is returned in the user’s language, avoiding direct quoting.

## 🧠 Prompt Logic Highlights
- Responds only with medical facts
- Ignores or filters non-medical questions
- Detects and replies in the user’s language
- Prefers internal documents, then supplements with web content
- Avoids hallucinations and general-purpose LLM errors