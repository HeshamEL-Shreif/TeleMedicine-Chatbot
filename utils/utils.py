from langchain.chat_models import init_chat_model
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.tools.tavily_search.tool import TavilySearchResults
import os
from dotenv import load_dotenv
from huggingface_hub import login
load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
search_tool = TavilySearchResults(k=3, tavily_api_key=os.getenv("TAVILY_API_KEY"))
llm = init_chat_model("meta-llama/llama-4-scout-17b-16e-instruct", model_provider="groq")
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")