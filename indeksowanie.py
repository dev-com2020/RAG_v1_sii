import chromadb
from sentence_transformers import SentenceTransformer

# --- 1. Inicjalizacja ---
# Używamy klienta ChromaDB, który działa w pamięci RAM
client = chromadb.PersistentClient(path='chroma_db')

# Model do tworzenia wektorów (embeddings). Wybierz model odpowiedni do języka polskiego.
# "all-MiniLM-L6-v2" jest szybki, ale lepszy dla angielskiego.
# "paraphrase-multilingual-MiniLM-L12-v2" jest lepszy dla wielu języków.
embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Tworzymy nową kolekcję (odpowiednik tabeli w SQL)
# Jeśli kolekcja już istnieje, zostanie użyta istniejąca.
collection = client.get_or_create_collection("regulaminy_firmy")

# --- 2. Ładowanie i dzielenie danych ---
print("Ładowanie i dzielenie danych...")
with open("dane.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Proste dzielenie tekstu na akapity (w praktyce używa się bardziej zaawansowanych metod)
chunks = [chunk for chunk in text.split("\n\n") if chunk.strip()]

# --- 3. Tworzenie wektorów i zapis do bazy ---
print(f"Tworzenie wektorów dla {len(chunks)} fragmentów...")

# Generujemy wektory dla każdego fragmentu
embeddings = embedding_model.encode(chunks).tolist()

# Tworzymy unikalne ID dla każdego fragmentu
ids = [f"chunk_{i}" for i in range(len(chunks))]

# Zapisujemy dane w ChromaDB
collection.add(
    embeddings=embeddings,
    documents=chunks,
    ids=ids
)

print("\n✓ Dane zostały zaindeksowane w ChromaDB!")
print(f"Liczba dokumentów w kolekcji: {collection.count()}")

# --- 4. Testowe wyszukiwanie ---
query = "Ile dni urlopu mi przysługuje?"

# Tworzymy wektor dla zapytania
query_embedding = embedding_model.encode([query]).tolist()

# Wyszukujemy 2 najbardziej podobne fragmenty
results = collection.query(
    query_embeddings=query_embedding,
    n_results=2
)

print("\n--- Wyniki testowego wyszukiwania dla zapytania: '{}' ---".format(query))
for i, doc in enumerate(results["documents"][0]):
    print(f"{i+1}. {doc.strip()}")
    print(f"   (Podobieństwo: {results["distances"][0][i]:.4f})")