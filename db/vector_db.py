from langchain_chroma import Chroma  # Updated import
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.utils import embedding_model
import os

VECTOR_DB_PATH = "./chroma_langchain_db"

def initialize_vector_store():
    return Chroma(
        collection_name="example_collection",
        embedding_function=embedding_model,
        persist_directory=VECTOR_DB_PATH,
    )

def load_documents_from_directory(directory_path):
    documents = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(directory_path, filename))
            docs = loader.load()
            documents.extend(docs)
    return documents

def split_documents(documents, chunk_size=1500, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return text_splitter.split_documents(documents)

def add_documents_to_vector_store(vector_store, documents):
    if not documents:
        print("No documents to add to the vector store.")
        return

    vector_store.add_documents(documents)
    print(f"Added {len(documents)} documents to the vector store.")

def save_docs_to_vector_store():
    vector_store = initialize_vector_store()

    directory_path = "./documents"
    documents = load_documents_from_directory(directory_path)

    if not documents:
        print("No documents found in the specified directory.")
        return

    split_docs = split_documents(documents)
    add_documents_to_vector_store(vector_store, split_docs)
    print("Vector store initialized and documents added successfully.")

def load_vector_store():
    return Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embedding_model,
    )