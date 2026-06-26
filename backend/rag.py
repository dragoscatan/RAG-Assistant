import os
from collections import Counter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

DB_PATH = "chroma_db"
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

embeddings_model = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_URL)
llm_client = Ollama(model="llama3.1", base_url=OLLAMA_URL)

template = """
You are a helpful and direct educational assistant. Use strictly the information from the context below to answer the question.
Take the Chat History into account if the user refers to previous concepts.

Context:
{context}

Chat History:
{history}

Question: {question}

CRITICAL INSTRUCTIONS FOR YOUR ANSWER:
- Provide a clear, natural, and direct answer based ONLY on the context.
- DO NOT use prefatory phrases like "Based on the provided context", "According to Document X", or "On Page Y".
- DO NOT include or repeat any citation numbers or brackets (such as [15], [20], etc.) that might appear in the text.
- Simply state the facts found in the text. If the text does not contain the answer, state that you don't have enough information. Do not invent anything.

Answer:
"""

prompt_template = PromptTemplate(template=template, input_variables=["context", "history", "question"])


def generate_answer(query: str, istoric: list = None):
    bazadate = Chroma(persist_directory=DB_PATH, embedding_function=embeddings_model)

    docs = bazadate.similarity_search(query, k=8)

    context_parts = []
    for doc in docs:
        nume_fisier = os.path.basename(doc.metadata.get('source', 'Document necunoscut'))
        fragment_etichetat = f"[Informație extrasă din documentul: {nume_fisier}]\n{doc.page_content}"
        context_parts.append(fragment_etichetat)

    context = "\n\n".join(context_parts)

    history_text = "Nu exista istoric."

    if istoric and len(istoric) > 0:
        ultimele_mesaje = istoric[-6:]
        history_lines = []
        for msg in ultimele_mesaje:
            rol = "Utilizator" if msg.get("tip") == "user" else "Asistent AI"
            text = msg.get("text", "")
            history_lines.append(f"{rol}: {text}")
        history_text = "\n".join(history_lines)

    formatted_prompt = prompt_template.format(context=context, history=history_text, question=query)

    #apelare model
    response = llm_client.invoke(formatted_prompt)
    final_answer = response.content if hasattr(response, "content") else str(response)
    print(f"\n[Backend LLM Response]:\n{final_answer}\n")

    #numarare pt sursa final
    numarator = Counter()
    for d in docs:
        nume_fisier = os.path.basename(d.metadata.get('source', 'Document necunoscut'))
        numarator[nume_fisier] += 1

    sources = []
    for nume, numar in numarator.items():
        sources.append({
            "document": nume,
            "fragmente_folosite": numar
        })

    return final_answer, sources