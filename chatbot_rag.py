import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import requests

# --- 1. Konfiguracja ---
# Sprawdź, który serwer jest aktywny i ustaw odpowiedni URL
OLLAMA_URL = "http://localhost:11434"
LM_STUDIO_URL = "http://localhost:1234"

api_url = ""
api_key = "ollama"  # Dla Ollama klucz jest dowolny, dla LM Studio też
model_name = "google/gemma-3-1b"  # Zmień, jeśli używasz innego modelu w Ollama/LM Studio

try:
    requests.get(OLLAMA_URL)
    api_url = f"{OLLAMA_URL}/v1"
    print("✓ Wykryto serwer Ollama.")
except requests.exceptions.ConnectionError:
    try:
        requests.get(LM_STUDIO_URL)
        api_url = f"{LM_STUDIO_URL}/v1"
        print("✓ Wykryto serwer LM Studio.")
    except requests.exceptions.ConnectionError:
        print("❌ Nie wykryto aktywnego serwera Ollama ani LM Studio.")
        print("Uruchom jeden z nich i spróbuj ponownie.")
        exit()

# Inicjalizacja klienta OpenAI, który będzie komunikował się z lokalnym serwerem
client = OpenAI(base_url=api_url, api_key=api_key)

# Inicjalizacja bazy wektorowej i modelu do tworzenia wektorów
chroma_client = chromadb.PersistentClient(path='chroma_db')
embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
collection = chroma_client.get_collection("regulaminy_firmy")


# --- 2. Funkcja RAG ---
def run_rag(query):
    print(f"\nZapytanie: {query}")

    # Krok 1: Wyszukiwanie w bazie wektorowej (Retrieval)
    print("\n1. Wyszukiwanie relevantnych informacji...")
    query_embedding = embedding_model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=2
    )

    retrieved_context = "\n\n---\n\n".join(results["documents"][0])
    print("   Znaleziony kontekst:")
    print("   " + retrieved_context.replace("\n", "\n   "))

    # Krok 2: Budowanie promptu z kontekstem (Augmentation)
    system_prompt = """
    Jesteś pomocnym asystentem AI o nazwie "Firmowy Bot". Twoim zadaniem jest odpowiadanie na pytania pracowników na podstawie dostarczonych fragmentów regulaminu.
    Odpowiadaj tylko i wyłącznie na podstawie dostarczonego kontekstu. Jeśli w kontekście nie ma odpowiedzi na pytanie, odpowiedz: "Przepraszam, ale nie znalazłem odpowiedzi na to pytanie w dostarczonych dokumentach."
    Bądź precyzyjny i trzymaj się faktów.
    """

    user_prompt = f"""
    Kontekst:
    ---
    {retrieved_context}
    ---

    Pytanie: {query}
    """

    # Krok 3: Generowanie odpowiedzi przez LLM (Generation)
    print("\n2. Generowanie odpowiedzi przez LLM...")
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,  # Niska temperatura dla bardziej precyzyjnych odpowiedzi
    )

    return response.choices[0].message.content


# --- 3. Uruchomienie ---
if __name__ == "__main__":
    # Przykład 1: Pytanie, na które jest odpowiedź w danych
    answer1 = run_rag("Ile dni urlopu mi przysługuje, jeśli pracuję w firmie 5 lat?")
    print(f"\nOdpowiedź Bota:\n{answer1}")
    print("=" * 50)

    # Przykład 2: Pytanie, na które jest odpowiedź w danych
    answer2 = run_rag("Czy mogę dostać dofinansowanie do okularów?")
    print(f"\nOdpowiedź Bota:\n{answer2}")
    print("=" * 50)

    # Przykład 3: Pytanie, na które NIE ma odpowiedzi w danych
    answer3 = run_rag("Jaki jest dress code w piątki?")
    print(f"\nOdpowiedź Bota:\n{answer3}")
    print("=" * 50)