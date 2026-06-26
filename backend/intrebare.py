import os
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.documents import Document

DB_PATH = "chroma_db"


def clean_text(text: str) -> str:
    referinte = [
        r'\nReferințe\n', r'\nReferences\n',
        r'\nNote\n', r'\nNotes\n',
        r'\nBibliografie\n', r'\nBibliography\n',
        r'\nVezi și\n', r'\nSee also\n'
    ]

    pozitie_minima = len(text)
    for pattern in referinte:
        match = re.search(pattern, text, re.IGNORECASE)
        if match and match.start() < pozitie_minima:
            pozitie_minima = match.start()

    t = text[:pozitie_minima]
    t = re.sub(r'\[\d+]', '', t)
    t = re.sub(r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[AP]M', '', t)
    t = re.sub(r'http[s]?://\S+', '', t)
    t = re.sub(r'.* - Wikipedia', '', t)
    t = t.replace('\n', ' ')
    t = re.sub(r'\s+', ' ', t)
    t = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', t)

    return t.strip()


def process_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    text_complet = "\n".join([doc.page_content for doc in docs])
    text_curatat = clean_text(text_complet)

    doc_final = Document(
        page_content=text_curatat,
        metadata={"source": os.path.basename(file_path)}
    )

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents([doc_final])

    OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_URL)

    db = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=DB_PATH)

    return len(splits)
