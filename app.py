import streamlit as st
import os
from utils import *
from langchain.embeddings import HuggingFaceEmbeddings 
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain

OPENAI_API_KEY = "Añadir OpenAI API Key"

st.set_page_config('preguntaDOC')
st.header("Pregunta a tu PDF")


with st.sidebar:
    
    archivos = load_name_files(FILE_LIST)
    files_uploaded = st.file_uploader(
        "Carga tu archivo",
        type="pdf",
        accept_multiple_files=True
        )
    
    if st.button('Procesar'):
        for pdf in files_uploaded:
            if pdf is not None and pdf.name not in archivos:
                archivos.append(pdf.name)
                text_to_chromadb(pdf)

        archivos = save_name_files(FILE_LIST, archivos)

    if len(archivos) > 0:
        st.write("Archivos cargados:")
        lista_documentos = st.empty()
        with lista_documentos.container():
            for arch in archivos:
                st.write(arch)
            if st.button('Borrar documentos'):
                archivos = []
                clean_files(FILE_LIST)
                lista_documentos.empty()

if archivos:
    user_question = st.text_input("Pregunta:")
    if user_question:
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )
        
        vstore = Chroma(client=chroma_client,
                        collection_name=INDEX_NAME,
                        embedding_function=embeddings)

        docs = vstore.similarity_search(user_question, 3)
        llm = ChatOpenAI(model_name='gpt-3.5-turbo')
        chain = load_qa_chain(llm, chain_type="stuff")
        respuesta = chain.run(input_documents=docs, question=user_question)

        st.write(respuesta)