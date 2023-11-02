
import os
import streamlit as st

import chromadb
import tempfile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings 


FILE_LIST = "archivos.txt"
INDEX_NAME = 'taller'

chroma_client = chromadb.HttpClient(host='localhost', port=8000)

def save_name_files(path, new_files):

    old_files = load_name_files(path)

    with open(path, "a") as file:
        for item in new_files:
            if item not in old_files:
                file.write(item + "\n")
                old_files.append(item)
    
    return old_files


def load_name_files(path):

    archivos = []
    with open(path, "r") as file:
        for line in file:
            archivos.append(line.strip())

    return archivos


def clean_files(path):
    with open(path, "w") as file:
        pass
    chroma_client.delete_collection(name=INDEX_NAME)
    collection = chroma_client.create_collection(name=INDEX_NAME)

    return True


def text_to_chromadb(pdf):

    temp_dir = tempfile.TemporaryDirectory()
    temp_filepath = os.path.join(temp_dir.name, pdf.name)
    with open(temp_filepath, "wb") as f:
        f.write(pdf.getvalue())

    loader = PyPDFLoader(temp_filepath)
    text = loader.load()

    with st.spinner(f'Creando embedding fichero: {pdf.name}'):
        create_embeddings(pdf.name, text)

    return True


def create_embeddings(file_name, text):
    print(f"Creando embeddings del archivo: {file_name}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        length_function=len
        )        
    
    chunks = text_splitter.split_documents(text)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
    
    Chroma.from_documents(
        chunks,
        embeddings,   
        client=chroma_client,
        collection_name=INDEX_NAME)
        
    return True
